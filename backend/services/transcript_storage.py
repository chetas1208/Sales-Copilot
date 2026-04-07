"""
Transcript Storage Service
Stores and retrieves meeting transcripts with word-level data
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TranscriptStorage:
    """Manages storage and retrieval of meeting transcripts"""

    def __init__(self, db_path: str = "transcripts.db"):
        """Initialize transcript storage with SQLite database"""
        self.db_path = db_path
        self.init_database()
        logger.info(f"Transcript storage initialized: {db_path}")

    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Meetings table - stores meeting metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id TEXT UNIQUE NOT NULL,
                meeting_url TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                total_duration_seconds REAL,
                total_words INTEGER DEFAULT 0,
                total_speakers INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)

        # Transcripts table - stores individual transcript segments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meeting_id INTEGER NOT NULL,
                bot_id TEXT NOT NULL,
                speaker_name TEXT,
                timestamp TIMESTAMP NOT NULL,
                new_text TEXT,
                transcript TEXT,
                utterance TEXT,
                end_of_turn BOOLEAN,
                turn_is_formatted BOOLEAN,
                transcription_mode TEXT,
                custom_attributes TEXT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meeting_id) REFERENCES meetings(id)
            )
        """)

        # Words table - stores word-level timing and confidence data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transcript_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                confidence REAL,
                speaker TEXT,
                punctuated_word TEXT,
                speech_confidence REAL,
                word_is_final BOOLEAN,
                FOREIGN KEY (transcript_id) REFERENCES transcripts(id)
            )
        """)

        # Create indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transcripts_bot_id ON transcripts(bot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transcripts_timestamp ON transcripts(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_transcript_id ON words(transcript_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_start_time ON words(start_time)")

        conn.commit()
        conn.close()

        logger.info("Database tables and indexes created/verified")

    def store_webhook_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a complete webhook payload

        Args:
            payload: The webhook payload from Meetstream

        Returns:
            Dictionary with storage result and IDs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Extract fields
            bot_id = payload.get("bot_id")
            speaker_name = payload.get("speakerName", payload.get("speaker", "Unknown"))
            timestamp = payload.get("timestamp")
            new_text = payload.get("new_text", "")
            transcript = payload.get("transcript", "")
            utterance = payload.get("utterance", "")
            end_of_turn = payload.get("end_of_turn", False)
            turn_is_formatted = payload.get("turn_is_formatted", False)
            transcription_mode = payload.get("transcription_mode", "")
            custom_attributes = json.dumps(payload.get("custom_attributes", {}))
            words = payload.get("words", [])

            # Ensure meeting exists
            meeting_id = self._ensure_meeting_exists(cursor, bot_id)

            # Insert transcript segment
            cursor.execute("""
                INSERT INTO transcripts (
                    meeting_id, bot_id, speaker_name, timestamp, new_text,
                    transcript, utterance, end_of_turn, turn_is_formatted,
                    transcription_mode, custom_attributes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meeting_id, bot_id, speaker_name, timestamp, new_text,
                transcript, utterance, end_of_turn, turn_is_formatted,
                transcription_mode, custom_attributes
            ))

            transcript_id = cursor.lastrowid

            # Insert words
            word_count = 0
            for word_data in words:
                cursor.execute("""
                    INSERT INTO words (
                        transcript_id, word, start_time, end_time, confidence,
                        speaker, punctuated_word, speech_confidence, word_is_final
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transcript_id,
                    word_data.get("word", ""),
                    word_data.get("start", 0),
                    word_data.get("end", 0),
                    word_data.get("confidence", 0),
                    word_data.get("speaker", ""),
                    word_data.get("punctuated_word", ""),
                    word_data.get("speech_confidence", 0),
                    word_data.get("word_is_final", False)
                ))
                word_count += 1

            # Update meeting statistics
            cursor.execute("""
                UPDATE meetings
                SET total_words = total_words + ?,
                    total_speakers = (
                        SELECT COUNT(DISTINCT speaker_name)
                        FROM transcripts
                        WHERE meeting_id = ?
                    )
                WHERE id = ?
            """, (word_count, meeting_id, meeting_id))

            conn.commit()
            conn.close()

            logger.info(f"Stored transcript segment: bot_id={bot_id}, transcript_id={transcript_id}, words={word_count}")

            return {
                "success": True,
                "meeting_id": meeting_id,
                "transcript_id": transcript_id,
                "word_count": word_count
            }

        except Exception as e:
            logger.error(f"Error storing webhook payload: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _ensure_meeting_exists(self, cursor, bot_id: str) -> int:
        """Ensure meeting record exists, create if not"""
        cursor.execute("SELECT id FROM meetings WHERE bot_id = ?", (bot_id,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # Create new meeting
        cursor.execute("""
            INSERT INTO meetings (bot_id) VALUES (?)
        """, (bot_id,))

        return cursor.lastrowid

    def get_meeting_by_bot_id(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting details by bot_id"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM meetings WHERE bot_id = ?
        """, (bot_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_transcripts_by_bot_id(self, bot_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all transcript segments for a meeting"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM transcripts
            WHERE bot_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        """, (bot_id, limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_words_for_transcript(self, transcript_id: int) -> List[Dict[str, Any]]:
        """Get all words for a specific transcript segment"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM words
            WHERE transcript_id = ?
            ORDER BY start_time ASC
        """, (transcript_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_full_transcript_text(self, bot_id: str) -> str:
        """Get complete transcript as formatted text"""
        transcripts = self.get_transcripts_by_bot_id(bot_id, limit=10000)

        lines = []
        current_speaker = None

        for t in transcripts:
            speaker = t.get("speaker_name", "Unknown")
            text = t.get("new_text") or t.get("transcript", "")

            if text.strip():
                if speaker != current_speaker:
                    lines.append(f"\n{speaker}:")
                    current_speaker = speaker
                lines.append(f"  {text}")

        return "\n".join(lines)

    def get_meeting_statistics(self, bot_id: str) -> Dict[str, Any]:
        """Get statistics for a meeting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get meeting info
        cursor.execute("""
            SELECT * FROM meetings WHERE bot_id = ?
        """, (bot_id,))
        meeting = cursor.fetchone()

        if not meeting:
            conn.close()
            return {"error": "Meeting not found"}

        # Get transcript count
        cursor.execute("""
            SELECT COUNT(*) FROM transcripts WHERE bot_id = ?
        """, (bot_id,))
        transcript_count = cursor.fetchone()[0]

        # Get speaker list
        cursor.execute("""
            SELECT DISTINCT speaker_name, COUNT(*) as segment_count
            FROM transcripts
            WHERE bot_id = ?
            GROUP BY speaker_name
            ORDER BY segment_count DESC
        """, (bot_id,))
        speakers = [{"name": row[0], "segments": row[1]} for row in cursor.fetchall()]

        # Get time range
        cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM transcripts
            WHERE bot_id = ?
        """, (bot_id,))
        time_range = cursor.fetchone()

        # Get average confidence
        cursor.execute("""
            SELECT AVG(confidence)
            FROM words w
            JOIN transcripts t ON w.transcript_id = t.id
            WHERE t.bot_id = ?
        """, (bot_id,))
        avg_confidence = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "bot_id": bot_id,
            "total_segments": transcript_count,
            "total_words": meeting[5],  # total_words column
            "total_speakers": meeting[6],  # total_speakers column
            "speakers": speakers,
            "started_at": time_range[0],
            "last_update": time_range[1],
            "average_confidence": round(avg_confidence * 100, 2) if avg_confidence else 0
        }

    def get_all_meetings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all meetings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM meetings
            ORDER BY started_at DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_transcripts(self, query: str, bot_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search transcripts by text content"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if bot_id:
            cursor.execute("""
                SELECT * FROM transcripts
                WHERE bot_id = ? AND (
                    new_text LIKE ? OR
                    transcript LIKE ? OR
                    utterance LIKE ?
                )
                ORDER BY timestamp DESC
                LIMIT ?
            """, (bot_id, f"%{query}%", f"%{query}%", f"%{query}%", limit))
        else:
            cursor.execute("""
                SELECT * FROM transcripts
                WHERE new_text LIKE ? OR
                      transcript LIKE ? OR
                      utterance LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def delete_meeting(self, bot_id: str) -> bool:
        """Delete a meeting and all its transcripts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get meeting_id
            cursor.execute("SELECT id FROM meetings WHERE bot_id = ?", (bot_id,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False

            meeting_id = result[0]

            # Delete words
            cursor.execute("""
                DELETE FROM words
                WHERE transcript_id IN (
                    SELECT id FROM transcripts WHERE meeting_id = ?
                )
            """, (meeting_id,))

            # Delete transcripts
            cursor.execute("DELETE FROM transcripts WHERE meeting_id = ?", (meeting_id,))

            # Delete meeting
            cursor.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))

            conn.commit()
            conn.close()

            logger.info(f"Deleted meeting: bot_id={bot_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting meeting: {str(e)}")
            return False


# Singleton instance
_transcript_storage = None

def get_transcript_storage() -> TranscriptStorage:
    """Get the singleton transcript storage instance"""
    global _transcript_storage
    if _transcript_storage is None:
        db_path = Path(__file__).parent.parent / "transcripts.db"
        _transcript_storage = TranscriptStorage(str(db_path))
    return _transcript_storage
