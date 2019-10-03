pyinstaller -F svision_client.py
mkdir -p bin
mv dist/svision_client bin
rm -rf build/ dist/ __pycache__/ svision_client.spec
cp configs.json bin
