# main.py

"""
Matrix Voice Assistant
A modern, intelligent voice-controlled assistant with transparent UI
"""

import sys
import argparse
from pathlib import Path


# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.brain import Matrix, MatrixConfig
from core.logger import initialize_logging, log_info, log_error


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Matrix Voice Assistant - Your AI-powered voice assistant"
    )
    
    parser.add_argument(
        '--no-ui',
        action='store_true',
        help='Run without graphical UI'
    )
    
    parser.add_argument(
        '--wake-word',
        type=str,
        default='matrix',
        help='Wake word to activate assistant (default: matrix)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=15,
        help='Timeout in seconds for listening (default: 15)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--no-context',
        action='store_true',
        help='Disable context management'
    )
    
    return parser.parse_args()


def print_banner():
    """Print startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗  ║
    ║         ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝  ║
    ║         ██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝   ║
    ║         ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗   ║
    ║         ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗  ║
    ║         ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝  ║
    ║                                                           ║
    ║              Voice Assistant - Version 2.0                ║
    ║           Your Intelligent AI-Powered Assistant          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()
    
    # Print banner
    print_banner()
    
    try:
        # Initialize logging
        print(f"📝 Initializing logging system...")
        initialize_logging(log_level=args.log_level)
        log_info("=" * 60)
        log_info("Matrix Voice Assistant Starting...")
        log_info("=" * 60)
        
        # Create configuration
        print(f"⚙️  Configuring Matrix...")
        config = MatrixConfig(
            wake_word=args.wake_word,
            timeout=args.timeout,
            enable_ui=not args.no_ui,
            enable_context=not args.no_context,
            voice_feedback=True
        )
        
        log_info(f"Configuration: Wake word='{config.wake_word}', "
                f"Timeout={config.timeout}s, UI={config.enable_ui}")
        
        # Initialize Matrix
        print(f"🤖 Initializing Matrix AI...")
        matrix = Matrix(config)
        
        print(f"✅ Matrix initialized successfully!")
        print(f"")
        print(f"Wake word: '{args.wake_word}'")
        print(f"Timeout: {args.timeout} seconds")
        print(f"UI enabled: {'Yes' if not args.no_ui else 'No'}")
        print(f"")
        print(f"Say '{args.wake_word}' to activate the assistant")
        print(f"Press Ctrl+C to exit")
        print(f"")
        print(f"=" * 60)
        
        # Start Matrix
        matrix.start()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Matrix...")
        log_info("Shutdown requested by user")
        
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        log_error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        print("Goodbye! 👋")
        log_info("Matrix shutdown complete")


if __name__ == "__main__":
    main()