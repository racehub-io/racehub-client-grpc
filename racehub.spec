# -*- mode: python ; coding: utf-8 -*-
import sys

block_cipher = None

# Determine if we're on macOS
is_mac = sys.platform == 'darwin'

# Server Analysis
server_a = Analysis(
    ['racehub_client_grpc/server.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['grpc'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Client Analysis
client_a = Analysis(
    ['test_client.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['grpc'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Server PYZ
server_pyz = PYZ(server_a.pure, server_a.zipped_data, cipher=block_cipher)

# Client PYZ
client_pyz = PYZ(client_a.pure, client_a.zipped_data, cipher=block_cipher)

if is_mac:
    # macOS Server App
    server_exe = EXE(
        server_pyz,
        server_a.scripts,
        [],
        exclude_binaries=True,
        name='racehub-server',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    
    # macOS Client App
    client_exe = EXE(
        client_pyz,
        client_a.scripts,
        [],
        exclude_binaries=True,
        name='racehub-client',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    
    # macOS Server Collection
    server_coll = COLLECT(
        server_exe,
        server_a.binaries,
        server_a.zipfiles,
        server_a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='racehub-server',
    )
    
    # macOS Client Collection
    client_coll = COLLECT(
        client_exe,
        client_a.binaries,
        client_a.zipfiles,
        client_a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='racehub-client',
    )
    
    # Optional: Create macOS .app bundles
    app_server = BUNDLE(
        server_coll,
        name='RaceHub Server.app',
        icon=None,
        bundle_identifier='com.racehub.server',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'True',  # Server can run in background
        },
    )
    
    app_client = BUNDLE(
        client_coll,
        name='RaceHub Client.app',
        icon=None,
        bundle_identifier='com.racehub.client',
        info_plist={
            'NSHighResolutionCapable': 'True'
        },
    )
else:
    # Windows Server EXE
    server_exe = EXE(
        server_pyz,
        server_a.scripts,
        server_a.binaries,
        server_a.zipfiles,
        server_a.datas,
        [],
        name='racehub-server',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )

    # Windows Client EXE
    client_exe = EXE(
        client_pyz,
        client_a.scripts,
        client_a.binaries,
        client_a.zipfiles,
        client_a.datas,
        [],
        name='racehub-client',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=True,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    ) 