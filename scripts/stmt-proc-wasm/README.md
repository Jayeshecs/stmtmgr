# Statement Processor WebAssembly

This project implements a WebAssembly module for processing bank statements, specifically for HDFC Bank account and credit card statements. The module is designed to handle transaction storage and export functionality, similar to the original Python implementation.

## Project Structure

- **src/**: Contains the source code for the WebAssembly module.
  - **lib.rs**: Entry point for the WebAssembly module.
  - **txn_store.rs**: Implements the transaction storage and export functionality.
  - **hdfc_bank_acct_processor.rs**: Processes HDFC Bank account statements.
  - **hdfc_credit_card_processor.rs**: Processes HDFC credit card statements.
  - **statement_processor.rs**: Defines the abstract base class for statement processors.
  - **tests/**: Contains unit tests for the statement processors.
    - **test_statement_processor_provider.rs**: Tests the functionality of the statement processor provider.

## Setup Instructions

A. **Install Rust**: Ensure you have Rust installed on your machine. You can install it from [rust-lang.org](https://www.rust-lang.org/).

B. **Install wasm-pack**: This project uses `wasm-pack` to build the WebAssembly module. You can install it using:
   ```
   cargo install wasm-pack
   ```

C. **Install LLVM**:

**For Windows**
1. Install LLVM (Includes Clang):

- Download the LLVM installer from the LLVM Pre-Built Binaries.
- Choose the appropriate version for your system (e.g., Windows (64-bit)).
- Run the installer and follow the setup instructions.

2. Add LLVM to PATH:

- During installation, ensure the option to add LLVM to your system's PATH is selected.
- Alternatively, manually add the LLVM bin directory (e.g., C:\Program Files\LLVM\bin) to your PATH environment variable.

3. Verify Installation:

- Open a Command Prompt or PowerShell and run:

```
clang --version
```
- You should see the version information for clang.

4. Alternative: Use Chocolatey (Package Manager):

- If you have Chocolatey installed, you can install LLVM with:

```
choco install llvm
```

**For macOS**
1. Install Xcode Command Line Tools:

- Open a terminal and run:
```
xcode-select --install
```
- This will install the clang compiler along with other development tools.

2. Verify Installation:

- Run the following command to check the installed version:
```
clang --version
```

**For Linux**
1. Install Clang Using Your Package Manager:

- On Ubuntu/Debian:
```
sudo apt update
sudo apt install clang
```
- On Fedora:
```
sudo dnf install clang
```
- On Arch Linux:
```
sudo pacman -S clang
```
2. Verify Installation:

```
clang --version
```

D. **Build the Project**: Navigate to the project directory and run:
   ```
   wasm-pack build
   ```

E. **Run unit tests**: Navigate to the project directory and run:
   ```
   wasm-pack test --chrome
   ```

F. **Integration**: After building, you can integrate the generated WebAssembly module into your JavaScript application.
_TODO_

## License

This project is licensed under the MIT License. See the LICENSE file for more details.