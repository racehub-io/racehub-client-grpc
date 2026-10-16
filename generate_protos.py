from grpc_tools import protoc
import os
import sys


def generate_protos():
    """Generate the gRPC Python code from proto files."""
    proto_file = "racehub.proto"

    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.join(current_dir, "racehub_client_grpc")

    # Remove existing generated files if they exist
    for file in ["racehub_pb2.py", "racehub_pb2_grpc.py"]:
        package_file = os.path.join(package_dir, file)
        if os.path.exists(package_file):
            os.remove(package_file)
        root_file = os.path.join(current_dir, file)
        if os.path.exists(root_file):
            os.remove(root_file)

    # Command to generate the gRPC code
    protoc.main(
        [
            "grpc_tools.protoc",
            f"--proto_path={current_dir}",
            f"--python_out={current_dir}",
            f"--grpc_python_out={current_dir}",
            os.path.join(current_dir, proto_file),
        ]
    )

    # Fix imports in generated files
    pb2_file = os.path.join(current_dir, "racehub_pb2.py")
    pb2_grpc_file = os.path.join(current_dir, "racehub_pb2_grpc.py")

    # Move files to the package directory
    os.rename(pb2_file, os.path.join(package_dir, "racehub_pb2.py"))
    os.rename(pb2_grpc_file, os.path.join(package_dir, "racehub_pb2_grpc.py"))

    # Fix the import in pb2_grpc
    with open(os.path.join(package_dir, "racehub_pb2_grpc.py"), "r") as f:
        content = f.read()

    content = content.replace(
        "import racehub_pb2 as racehub__pb2",
        "from . import racehub_pb2 as racehub__pb2",
    )

    with open(os.path.join(package_dir, "racehub_pb2_grpc.py"), "w") as f:
        f.write(content)

    print("Generated gRPC code successfully!")


if __name__ == "__main__":
    generate_protos()
