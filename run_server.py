#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple server runner for Nextor AI Assistant
"""

if __name__ == "__main__":
    import logging
    from waitress import serve
    from app import create_app
    
    logger = logging.getLogger(__name__)
    
    # Create the Flask app
    app = create_app()
    
    port = 5000
    print(f"\n{'='*60}")
    print(f"🚀 Nextor AI Assistant Server")
    print(f"{'='*60}")
    print(f"📡 Server URL: http://127.0.0.1:{port}")
    print(f"📡 Server URL: http://localhost:{port}")
    print(f"{'='*60}")
    print(f"Press Ctrl+C to stop the server")
    print(f"{'='*60}\n")
    
    # Use Waitress server
    try:
        print(f"🔧 Starting Waitress server...")
        serve(app, host='127.0.0.1', port=port, threads=4, _quiet=False)
        print(f"⚠️ Serve function returned (this shouldn't happen unless server stopped)")
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except OSError as e:
        print(f"\n❌ Port binding error: {e}")
        print(f"💡 Tip: Port {port} may be in use or blocked by firewall")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 Server shutdown complete")
