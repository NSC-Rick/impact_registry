"""
Test script to verify Streamlit version supports st.Page and st.navigation APIs

This script checks:
1. Streamlit version is >= 1.36.0
2. st.Page API is available
3. st.navigation API is available
"""
import sys

def test_streamlit_version():
    """Test that Streamlit version supports navigation APIs"""
    try:
        import streamlit as st
        from packaging import version
        
        print(f"✓ Streamlit imported successfully")
        print(f"  Version: {st.__version__}")
        
        # Check version
        min_version = "1.36.0"
        current_version = st.__version__
        
        if version.parse(current_version) >= version.parse(min_version):
            print(f"✓ Streamlit version {current_version} >= {min_version}")
        else:
            print(f"✗ Streamlit version {current_version} < {min_version}")
            print(f"  Navigation APIs require Streamlit >= {min_version}")
            return False
        
        # Check st.Page exists
        if hasattr(st, 'Page'):
            print(f"✓ st.Page API available")
        else:
            print(f"✗ st.Page API not found")
            return False
        
        # Check st.navigation exists
        if hasattr(st, 'navigation'):
            print(f"✓ st.navigation API available")
        else:
            print(f"✗ st.navigation API not found")
            return False
        
        print("\n✅ All checks passed - Navigation APIs are supported")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import Streamlit: {e}")
        return False
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_streamlit_version()
    sys.exit(0 if success else 1)
