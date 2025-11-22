import zipfile
import os
import shutil
from pathlib import Path

# Config
APK_FILE = "grab.apk"  # Replace with your APK file
OUTPUT_DIR = "apk_extracted"
FLUTTER_ASSETS_OUTPUT = "flutter_assets_extracted"
REACT_NATIVE_ASSETS_OUTPUT = "react_native_assets_extracted"

def extract_apk(apk_path, output_dir):
    """Extracts APK contents into a directory."""
    print(f"Extracting {apk_path}...")
    try:
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        print(f"APK extracted to: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ Error extracting APK: {e}")
        return False

def is_flutter_app(extracted_dir):
    """Checks if the APK is built with Flutter."""
    flutter_assets = os.path.join(extracted_dir, "assets", "flutter_assets")
    flutter_lib = os.path.join(extracted_dir, "lib", "armeabi-v7a", "libflutter.so")  # Check for common architecture
    return os.path.exists(flutter_assets) or os.path.exists(flutter_lib)

def is_react_native_app(extracted_dir):
    """Checks if the APK is built with React Native."""
    js_bundle = os.path.join(extracted_dir, "assets", "index.android.bundle")
    rn_signature = os.path.join(extracted_dir, "lib", "armeabi-v7a", "libreactnativejni.so")
    return os.path.exists(js_bundle) or os.path.exists(rn_signature)

def copy_flutter_assets(extracted_dir, output_dir):
    """Copies Flutter assets (images, fonts, etc.) for reuse."""
    flutter_assets_src = os.path.join(extracted_dir, "assets", "flutter_assets")
    if not os.path.exists(flutter_assets_src):
        print("❌ No Flutter assets found!")
        return False

    print("✅ Found Flutter assets! Copying for reuse...")
    os.makedirs(output_dir, exist_ok=True)

    # Copy important directories
    asset_dirs = ["assets", "fonts", "packages"]
    for asset_dir in asset_dirs:
        src_path = os.path.join(flutter_assets_src, asset_dir)
        if os.path.exists(src_path):
            shutil.copytree(src_path, os.path.join(output_dir, asset_dir), dirs_exist_ok=True)
            print(f"📂 Copied: {asset_dir}")

    # Copy pubspec.yaml if available
    pubspec_src = os.path.join(flutter_assets_src, "pubspec.yaml")
    if os.path.exists(pubspec_src):
        shutil.copy(pubspec_src, os.path.join(output_dir, "pubspec.yaml"))
        print("📄 Copied: pubspec.yaml")

    print(f"🎉 Flutter assets extracted to: {output_dir}")
    return True

def copy_react_native_assets(extracted_dir, output_dir):
    """Copies React Native assets and JS bundle for reuse."""
    rn_assets_src = os.path.join(extracted_dir, "assets")
    js_bundle = os.path.join(extracted_dir, "assets", "index.android.bundle")

    if not os.path.exists(rn_assets_src):
        print("❌ No React Native assets found!")
        return False

    print("✅ Found React Native assets! Copying for reuse...")
    os.makedirs(output_dir, exist_ok=True)

    # Copy assets directory
    if os.path.exists(rn_assets_src):
        shutil.copytree(rn_assets_src, os.path.join(output_dir, "assets"), dirs_exist_ok=True)
        print("📂 Copied: assets")

    # Copy JS bundle
    if os.path.exists(js_bundle):
        shutil.copy(js_bundle, os.path.join(output_dir, "index.android.bundle"))
        print("📄 Copied: index.android.bundle")

    print(f"🎉 React Native assets extracted to: {output_dir}")
    return True

def main():
    # Step 1: Extract APK
    if not extract_apk(APK_FILE, OUTPUT_DIR):
        print("❌ APK extraction failed. Exiting.")
        return

    # Step 2: Check framework
    if is_flutter_app(OUTPUT_DIR):
        print("✅ This is a Flutter app!")
        copy_flutter_assets(OUTPUT_DIR, FLUTTER_ASSETS_OUTPUT)
        print("\n🔹 Next Steps for Flutter:")
        print("- Rebuild UI using extracted assets in 'flutter_assets_extracted/'")
        print("- Use 'flutter create' to start a new project")
        print("- Check 'pubspec.yaml' for dependencies (if extracted)")
        print("- Manually rewrite Dart logic (compiled code in libflutter.so is not recoverable)")
    elif is_react_native_app(OUTPUT_DIR):
        print("✅ This is a React Native app!")
        copy_react_native_assets(OUTPUT_DIR, REACT_NATIVE_ASSETS_OUTPUT)
        print("\n🔹 Next Steps for React Native:")
        print("- Rebuild UI using extracted assets in 'react_native_assets_extracted/'")
        print("- Use 'npx react-native init' to start a new project")
        print("- Analyze 'index.android.bundle' with a JS deobfuscator (e.g., JStillery)")
        print("- Manually rewrite JS/TS logic if bundle is obfuscated")
    else:
        print("❌ Not a Flutter or React Native app (no signatures found).")

    print("\n🔹 General Notes:")
    print("- Use 'apktool d app.apk' to extract resources and manifest for further analysis")
    print("- Rebuilding the app requires manual recreation of logic and UI")
    print("- Consider legal/ethical implications of decompiling APKs")

if __name__ == "__main__":
    main()