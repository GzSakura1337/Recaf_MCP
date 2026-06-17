"""
Recaf MCP Server - Bytecode Edit Tools

Full bytecode editing: list/modify instructions, assemble JASM text,
edit access flags, add/remove methods and fields, try-catch blocks,
replace class bytes, and save workspace. All mutations use POST.
"""

from src.server.config import get_from_recaf, post_to_recaf


# ── instruction listing ─────────────────────────────────────────────────

async def list_method_instructions(
    class_name: str, method_name: str, descriptor: str = ""
) -> dict:
    """Return every instruction in a method as a flat JSON array."""
    params = {"class_name": class_name, "method_name": method_name}
    if descriptor:
        params["descriptor"] = descriptor
    return await get_from_recaf("method/instructions", params)


# ── method body replacement (JSON) ──────────────────────────────────────

async def replace_method_body(
    class_name: str,
    method_name: str,
    instructions: list,
    descriptor: str = "",
) -> dict:
    """
    Replace the entire body of a method with a list of instruction dicts.
    Each dict has "opcode" and optional "args":
        {"opcode": "ALOAD", "args": [0]}
        {"opcode": "ICONST_1"}
        {"opcode": "INVOKEVIRTUAL", "args": ["java/io/PrintStream", "println", "(Ljava/lang/String;)V"]}
    Jump targets are integer indices into the list.
    """
    return await post_to_recaf("method/replace-body", {
        "class_name": class_name,
        "method_name": method_name,
        "descriptor": descriptor,
        "instructions": instructions,
    })


# ── JASM text assembly ──────────────────────────────────────────────────

async def assemble_method(
    class_name: str,
    method_name: str,
    text: str,
    descriptor: str = "",
) -> dict:
    """
    Assemble a method body from JASM-like text.

    One instruction per line:
        ALOAD 0
        GETFIELD com/example/Cls.field : I
        ICONST_1
        IADD
        PUTFIELD com/example/Cls.field : I
        RETURN

    Jump targets are label names:  GOTO L0
    Labels are defined with:       LABEL L0
    Try-catch:                     TRYCATCH L0 L1 L2 java/lang/Exception
    Line numbers:                  LINE 42
    Comments start with # or //.
    MAXSTACK/MAXLOCALS/FRAME/LOCALVARIABLE lines are ignored.
    """
    return await post_to_recaf("method/assemble", {
        "class_name": class_name,
        "method_name": method_name,
        "descriptor": descriptor,
        "text": text,
    })


# ── single instruction ops ──────────────────────────────────────────────

async def replace_instruction(
    class_name: str, method_name: str, index: int,
    instruction: dict, descriptor: str = "",
) -> dict:
    """Replace a single instruction at the given index."""
    return await post_to_recaf("method/instructions/replace", {
        "class_name": class_name, "method_name": method_name,
        "descriptor": descriptor, "index": index, "instruction": instruction,
    })


async def insert_instruction(
    class_name: str, method_name: str, index: int,
    instruction: dict, descriptor: str = "",
) -> dict:
    """Insert a new instruction at the given index."""
    return await post_to_recaf("method/instructions/insert", {
        "class_name": class_name, "method_name": method_name,
        "descriptor": descriptor, "index": index, "instruction": instruction,
    })


async def remove_instruction(
    class_name: str, method_name: str, index: int, descriptor: str = "",
) -> dict:
    """Remove the instruction at the given index."""
    return await post_to_recaf("method/instructions/remove", {
        "class_name": class_name, "method_name": method_name,
        "descriptor": descriptor, "index": index,
    })


# ── access flags ────────────────────────────────────────────────────────

async def edit_class_access(
    class_name: str,
    set_flags: list = None,
    clear_flags: list = None,
) -> dict:
    """
    Set or clear access flags on a class.
    Valid flags: public, private, protected, static, final, interface,
                 abstract, synthetic, annotation, enum.
    """
    return await post_to_recaf("class/edit-access", {
        "class_name": class_name,
        "set_flags": set_flags or [],
        "clear_flags": clear_flags or [],
    })


async def edit_method_access(
    class_name: str,
    method_name: str,
    set_flags: list = None,
    clear_flags: list = None,
    descriptor: str = "",
) -> dict:
    """
    Set or clear access flags on a method.
    Valid flags: public, private, protected, static, final, synchronized,
                 bridge, varargs, native, abstract, strictfp, synthetic.
    """
    return await post_to_recaf("method/edit-access", {
        "class_name": class_name,
        "method_name": method_name,
        "descriptor": descriptor,
        "set_flags": set_flags or [],
        "clear_flags": clear_flags or [],
    })


async def edit_field_access(
    class_name: str,
    field_name: str,
    set_flags: list = None,
    clear_flags: list = None,
    descriptor: str = "",
) -> dict:
    """
    Set or clear access flags on a field.
    Valid flags: public, private, protected, static, final, volatile,
                 transient, synthetic, enum.
    """
    return await post_to_recaf("field/edit-access", {
        "class_name": class_name,
        "field_name": field_name,
        "descriptor": descriptor,
        "set_flags": set_flags or [],
        "clear_flags": clear_flags or [],
    })


# ── class bytes ─────────────────────────────────────────────────────────

async def replace_class_bytes(class_name: str, bytes_base64: str) -> dict:
    """Replace a class entirely from base64-encoded class file bytes."""
    return await post_to_recaf("class/replace-bytes", {
        "class_name": class_name,
        "bytes_base64": bytes_base64,
    })


# ── add / remove methods ────────────────────────────────────────────────

async def add_method(
    class_name: str,
    method_name: str,
    descriptor: str,
    access: list = None,
    instructions: list = None,
) -> dict:
    """
    Add a new method to a class.
    `access`: list of flag strings (["public", "static"])
    `instructions`: optional list of instruction dicts for the body.
    """
    return await post_to_recaf("method/add", {
        "class_name": class_name,
        "method_name": method_name,
        "descriptor": descriptor,
        "access": access or [],
        "instructions": instructions or [],
    })


async def remove_method(
    class_name: str, method_name: str, descriptor: str = "",
) -> dict:
    """Remove a method from a class."""
    return await post_to_recaf("method/remove", {
        "class_name": class_name,
        "method_name": method_name,
        "descriptor": descriptor,
    })


# ── add / remove fields ─────────────────────────────────────────────────

async def add_field(
    class_name: str,
    field_name: str,
    descriptor: str,
    access: list = None,
    signature: str = None,
    value=None,
) -> dict:
    """
    Add a new field to a class.
    `access`: list of flag strings (["public", "static"])
    `value`: optional initial value (int or string).
    """
    return await post_to_recaf("field/add", {
        "class_name": class_name,
        "field_name": field_name,
        "descriptor": descriptor,
        "access": access or [],
        "signature": signature,
        "value": value,
    })


async def remove_field(
    class_name: str, field_name: str, descriptor: str = "",
) -> dict:
    """Remove a field from a class."""
    return await post_to_recaf("field/remove", {
        "class_name": class_name,
        "field_name": field_name,
        "descriptor": descriptor,
    })


# ── try-catch ───────────────────────────────────────────────────────────

async def set_try_catch_blocks(
    class_name: str,
    method_name: str,
    try_catch_blocks: list,
    descriptor: str = "",
) -> dict:
    """
    Set try-catch blocks for a method.

    Each block is a dict: {"start": "L0", "end": "L1", "handler": "L2", "type": "java/lang/Exception"}
    The `type` field is optional (null = finally / catch-all).
    Labels must exist in the method's instruction list.
    """
    return await post_to_recaf("method/try-catch", {
        "class_name": class_name,
        "method_name": method_name,
        "descriptor": descriptor,
        "try_catch_blocks": try_catch_blocks,
    })


# ── save workspace ──────────────────────────────────────────────────────

async def save_workspace(output_path: str) -> dict:
    """
    Export the (possibly modified) workspace back to disk, overwriting
    the target file if it exists.
    """
    return await post_to_recaf("workspace/save", {"output_path": output_path})
