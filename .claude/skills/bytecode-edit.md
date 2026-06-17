---
name: bytecode-edit
description: Recaf MCP bytecode editing — read, modify, and write JVM bytecode via MCP tools. Use when asked to change bytecode instructions, patch methods, edit access flags, add/remove methods or fields, modify try-catch blocks, or apply JASM assembly.
metadata:
  type: project
---

# Recaf MCP Bytecode Editing

Two families of tools: **read** (inspect) and **write** (mutate).

## Read Tools

| Tool | Returns |
|---|---|
| `list_method_instructions(class_name, method_name, descriptor?)` | JSON array of every instruction with index, opcode, args |
| `get_method_bytecode(class_name, method_name, descriptor?)` | ASM Textifier text (human-readable bytecode) |

## Write Tools

### Method body (high-level, preferred)

| Tool | Input |
|---|---|
| `assemble_method(class_name, method_name, text, descriptor?)` | JASM text → bytecode |
| `replace_method_body(class_name, method_name, instructions, descriptor?)` | JSON instruction list → bytecode |

### Single instruction

| Tool | Input |
|---|---|
| `replace_instruction(class_name, method_name, index, instruction, descriptor?)` | Replace one insn |
| `insert_instruction(class_name, method_name, index, instruction, descriptor?)` | Insert at position |
| `remove_instruction(class_name, method_name, index, descriptor?)` | Remove at index |

### Access flags

| Tool | Input |
|---|---|
| `edit_class_access(class_name, set_flags?, clear_flags?)` | List of flag strings |
| `edit_method_access(class_name, method_name, set_flags?, clear_flags?, descriptor?)` | List of flag strings |
| `edit_field_access(class_name, field_name, set_flags?, clear_flags?, descriptor?)` | List of flag strings |

Valid flags: `public`, `private`, `protected`, `static`, `final`, `synchronized`, `volatile`, `transient`, `native`, `interface`, `abstract`, `strictfp`, `synthetic`, `annotation`, `enum`, `bridge`, `varargs`.

### Method/field CRUD

| Tool | Notes |
|---|---|
| `add_method(class_name, method_name, descriptor, access?, instructions?)` | Instructions are JSON list; use `[]` for empty body |
| `remove_method(class_name, method_name, descriptor?)` | — |
| `add_field(class_name, field_name, descriptor, access?, signature?, value?)` | value: int or string initializer |
| `remove_field(class_name, field_name, descriptor?)` | — |

### Try-catch

| Tool | Input |
|---|---|
| `set_try_catch_blocks(class_name, method_name, try_catch_blocks, descriptor?)` | Array of `{"start":"L0","end":"L1","handler":"L2","type":"java/lang/Exception"}` |

### Class-level & workspace

| Tool | Notes |
|---|---|
| `replace_class_bytes(class_name, bytes_base64)` | Full class replacement from base64 bytes |
| `save_workspace(output_path)` | Export modified workspace to disk |

---

## Instruction Format (JSON)

Used by `replace_method_body`, `replace_instruction`, `insert_instruction`, `add_method`.

```json
{"opcode": "ALOAD", "args": [0]}
{"opcode": "BIPUSH", "args": [10]}
{"opcode": "NEW", "args": ["java/lang/String"]}
{"opcode": "GETFIELD", "args": ["com/example/Cls", "fieldName", "I"]}
{"opcode": "INVOKEVIRTUAL", "args": ["java/io/PrintStream", "println", "(Ljava/lang/String;)V"]}
{"opcode": "LDC", "args": ["hello"]}
{"opcode": "LDC", "args": [42]}
{"opcode": "GOTO", "args": [5]}
{"opcode": "IFEQ", "args": [3]}
{"opcode": "ICONST_0"}
{"opcode": "RETURN"}
```

Rules:
- **No-arg** opcodes omit `args`: `ICONST_0`, `RETURN`, `DUP`, `IADD`, `ARRAYLENGTH`, etc.
- **Var** instructions: `args: [varIndex]`
- **Int**: `args: [operand]`
- **Type**: `args: ["internal/type/name"]`
- **Field**: `args: [owner, name, descriptor]` — all internal form
- **Method**: `args: [owner, name, descriptor]` — all internal form
- **Jump**: `args: [targetIndex]` — integer index in the instruction list
- **LDC**: `args: [intValue]` or `args: ["string"]`
- **IINC**: `args: [varIndex, increment]`
- **LINENUMBER**: `args: [lineNumber]`
- Labels and frames are auto-generated — do NOT include them.

## Instruction Format (JASM Text)

Used by `assemble_method`. One instruction per line.

```
# Comments start with # or //
ALOAD 0
GETFIELD com/example/Cls.field : I        # field: owner/Name.name : desc
ICONST_1
IADD
PUTFIELD com/example/Cls.field : I
RETURN
```

With control flow:
```
LABEL L0
ALOAD 0
IFNULL L1
ICONST_0
GOTO L2
LABEL L1
ICONST_1
LABEL L2
RETURN
```

With try-catch and line numbers:
```
LINE 10
NEW java/lang/Exception
DUP
INVOKESPECIAL java/lang/Exception.<init> ()V
ATHROW
TRYCATCH L0 L1 L2 java/lang/Exception
```

Key points:
- `ALOAD 0`, `ILOAD 1`, `ISTORE 0`, etc. for var instructions
- `BIPUSH 10`, `SIPUSH 1000` for int constants
- `NEW java/lang/String` for type references
- `GETFIELD com/example/Cls.field : I` for field access (note ` : ` separator)
- `INVOKEVIRTUAL java/io/PrintStream.println (Ljava/lang/String;)V` for method calls
- `GOTO L0`, `IFEQ L0`, `IFNE L1`, etc. for jumps
- `LDC "hello"` or `LDC 42` or `LDC 3.14` for constants
- `IINC 0 1` for local variable increment
- `LINE 42` for line number hints
- `LABEL name` to define explicit labels (auto-generated if omitted)

## Workflow Patterns

### Pattern 1: Read → Modify → Assemble (text round-trip)

```
1. get_method_bytecode(class_name, method_name, descriptor)
2. Edit the returned text
3. assemble_method(class_name, method_name, text, descriptor)
```

This is the **recommended** approach for most edits. The LLM reads Textifier output, modifies the text, and assembles it back.

### Pattern 2: Read → Edit JSON → Replace (structured round-trip)

```
1. list_method_instructions(class_name, method_name, descriptor)
2. Modify the returned JSON array
3. replace_method_body(class_name, method_name, instructions, descriptor)
```

Better for programmatic edits (e.g., "change all ICONST_0 to ICONST_1").

### Pattern 3: Single instruction (small targeted edits)

```
1. list_method_instructions(class_name, method_name, descriptor)
2. Identify the index of the instruction to change
3. replace_instruction(class_name, method_name, index, {"opcode": "ICONST_1"}, descriptor)
```

### Pattern 4: Change access / add methods

```
edit_class_access("com.example.Cls", set_flags=["public"])
edit_method_access("com.example.Cls", "secretFunc", set_flags=["public"])
add_method("com.example.Cls", "newMethod", "()V", access=["public"], instructions=[...])
```

### Pattern 5: Full class replacement

```
get_raw_class_bytes(class_name)  →  base64
# Modify bytes with external tool
replace_class_bytes(class_name, modified_base64)
```

## Common Use Cases

**Remove a null check:**
```
1. list_method_instructions(class_name, method_name)
2. Find the IFNULL + branch instructions
3. remove_instruction for the IFNULL and the null-handling block
```

**Change return value:**
```
1. list_method_instructions(class_name, method_name)
2. Find the return sequence (ICONST_0 + IRETURN)
3. replace_instruction to change ICONST_0 → ICONST_1
```

**Make private method public:**
```
edit_method_access(class_name, method_name, set_flags=["public"], clear_flags=["private"])
```

**Inject a System.out.println at method entry:**
```
assemble_method(class_name, method_name, text="""
    GETSTATIC java/lang/System.out : Ljava/io/PrintStream;
    LDC "DEBUG: entering method"
    INVOKEVIRTUAL java/io/PrintStream.println (Ljava/lang/String;)V
    ...existing instructions...
""")
```

## Important Notes

- All class names use **dot-separated** external form: `com.example.MyClass`
- Internal names (slashes) are used within instruction operands: `com/example/MyClass`
- JVM descriptors: `(args)return`, e.g., `(ILjava/lang/String;)V`
- All mutations are **immediate** in the workspace — use `save_workspace` to persist
- Use `get_modified_classes` to check what's been changed
- Use `revert_class` to undo changes to a specific class
- Try-catch labels must reference existing label nodes in the method's instruction list
