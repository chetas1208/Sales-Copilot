"""
Example: RAG-Powered Sales Conversation
Demonstrates how the Meetstream bot uses RAG to answer customer questions in real-time
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_service import get_rag_service


class MockSalesConversation:
    """Simulates a sales conversation with RAG-powered responses"""

    def __init__(self):
        self.rag = get_rag_service()
        self.conversation_history = []

    def print_separator(self, char="─", length=80):
        """Print a separator line"""
        print(char * length)

    def print_speaker(self, speaker: str, message: str, color_code: str = ""):
        """Print a formatted speaker message"""
        reset = "\033[0m"
        if color_code:
            print(f"\n{color_code}{speaker}:{reset}")
        else:
            print(f"\n{speaker}:")
        print(f"  {message}")

    async def customer_asks(self, question: str):
        """Customer asks a question"""
        self.print_speaker("👤 Customer", question, "\033[94m")  # Blue
        self.conversation_history.append({"role": "customer", "message": question})

        # Bot processes with RAG
        await asyncio.sleep(0.5)  # Simulate processing time
        return await self.bot_responds(question)

    async def bot_responds(self, question: str):
        """Bot generates RAG-powered response"""
        result = self.rag.answer_question(question)

        confidence_emoji = {
            "high": "✅",
            "medium": "ℹ️",
            "low": "⚠️",
            "none": "❌"
        }

        emoji = confidence_emoji.get(result["confidence"], "💬")

        self.print_speaker(
            f"🤖 Meetstream Bot {emoji}",
            result["answer"],
            "\033[92m"  # Green
        )

        # Show confidence level
        print(f"\n  [Confidence: {result['confidence']} | Source: {result['source']}]")

        self.conversation_history.append({
            "role": "bot",
            "message": result["answer"],
            "confidence": result["confidence"]
        })

        return result

    async def simulate_conversation(self):
        """Simulate a realistic sales conversation"""

        print("\n" + "="*80)
        print("  SALES CALL SIMULATION - RAG-Powered Bot Demo")
        print("  TechCorp Enterprise Solutions")
        print("="*80)

        # Introduction
        self.print_speaker(
            "👤 Customer",
            "Hi, I'm looking for a cloud monitoring solution for my company. What do you offer?",
            "\033[94m"
        )
        self.print_separator()

        await self.customer_asks(
            "What cloud monitoring solutions do you have?"
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Follow-up: Features
        await self.customer_asks(
            "What are the key features of Cloud Monitor Pro?"
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Follow-up: Pricing
        await self.customer_asks(
            "What's the pricing for Cloud Monitor Pro?"
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Additional interest: Cost optimization
        await self.customer_asks(
            "We're also spending too much on cloud resources. Can you help with that?"
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Pricing for cost optimizer
        await self.customer_asks(
            "How does the Cost Optimizer AI pricing work?"
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Security concerns
        await self.customer_asks(
            "What about security and compliance? We need to meet SOC2 and HIPAA requirements."
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Bundle pricing
        await self.customer_asks(
            "If we buy all three CloudOps modules, do you offer any bundle discounts?"
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Trial question
        await self.customer_asks(
            "Can we try this before committing to a purchase?"
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Enterprise support
        await self.customer_asks(
            "We're a large enterprise with about 500 servers. What level of support would we get?"
        )
        self.print_separator()

        await asyncio.sleep(1)

        # Next steps
        await self.customer_asks(
            "This sounds great! How do we get started?"
        )
        self.print_separator()

        # Summary
        print("\n" + "="*80)
        print("  CONVERSATION SUMMARY")
        print("="*80)

        total_questions = len([h for h in self.conversation_history if h["role"] == "customer"])
        high_confidence = len([h for h in self.conversation_history if h["role"] == "bot" and h.get("confidence") == "high"])

        print(f"\n📊 Statistics:")
        print(f"  • Total questions answered: {total_questions}")
        print(f"  • High confidence answers: {high_confidence}/{total_questions} ({100*high_confidence//total_questions}%)")
        print(f"\n✨ Key Topics Covered:")
        print(f"  • Cloud monitoring features and capabilities")
        print(f"  • Pricing for multiple modules")
        print(f"  • Cost optimization solutions")
        print(f"  • Security and compliance features")
        print(f"  • Bundle discounts")
        print(f"  • Trial options and support levels")

        print(f"\n💡 Outcome:")
        print(f"  Customer received comprehensive product information")
        print(f"  All questions answered with RAG-powered responses")
        print(f"  Bot provided accurate pricing and feature details")
        print(f"  Customer ready to start 14-day free trial!")

        print("\n" + "="*80 + "\n")


async def main():
    """Run the sales conversation simulation"""
    try:
        print("\n🚀 Initializing RAG-powered sales bot...")
        conversation = MockSalesConversation()
        print("✅ Bot ready!\n")

        await conversation.simulate_conversation()

    except KeyboardInterrupt:
        print("\n\n⚠️  Conversation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
