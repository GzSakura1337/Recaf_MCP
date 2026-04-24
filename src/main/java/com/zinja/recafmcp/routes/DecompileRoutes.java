package com.zinja.recafmcp.routes;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import software.coley.recaf.info.JvmClassInfo;
import software.coley.recaf.path.ClassPathNode;
import software.coley.recaf.services.decompile.DecompileResult;
import software.coley.recaf.services.decompile.DecompilerManager;
import software.coley.recaf.services.decompile.JvmDecompiler;
import software.coley.recaf.services.workspace.WorkspaceManager;
import software.coley.recaf.workspace.model.Workspace;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

public class DecompileRoutes {
    private final WorkspaceManager wm;
    private final DecompilerManager dm;

    public DecompileRoutes(WorkspaceManager wm, DecompilerManager dm) {
        this.wm = wm;
        this.dm = dm;
    }

    public void register(McpHttpServer server) {
        server.get("/decompilers", (req, res) -> {
            JsonArray arr = new JsonArray();
            JvmDecompiler active = dm.getTargetJvmDecompiler();
            for (JvmDecompiler d : dm.getJvmDecompilers()) {
                JsonObject o = new JsonObject();
                o.addProperty("name", d.getName());
                o.addProperty("version", d.getVersion());
                o.addProperty("active", d == active);
                arr.add(o);
            }
            JsonObject out = new JsonObject();
            out.add("decompilers", arr);
            res.json(out);
        });

        server.post("/decompilers/active", (req, res) -> {
            // TODO: DecompilerManager exposes getTargetJvmDecompiler() but no
            // public setter — the Recaf config service (DecompilerManagerConfig)
            // is where the active decompiler is persisted. Inject that here and
            // call its setTargetJvmDecompiler(String) when available.
            res.status(501).json(JsonResponses.error(
                    "active-decompiler switch requires injecting DecompilerManagerConfig and updating its target field"));
        });

        server.get("/class-source", (req, res) -> decompileAndRespond(req.query("class_name"), req.query("decompiler"), res));
        server.get("/decompile", (req, res) -> decompileAndRespond(req.query("class_name"), req.query("decompiler"), res));
    }

    private void decompileAndRespond(String className, String decompiler, com.zinja.recafmcp.http.Response res) throws Exception {
        Workspace ws = wm.getCurrent();
        if (ws == null) { res.status(409).json(JsonResponses.error("no workspace open")); return; }
        if (className == null || className.isEmpty()) {
            res.status(400).json(JsonResponses.error("missing 'class_name'"));
            return;
        }
        ClassPathNode node = ws.findJvmClass(className.replace('.', '/'));
        if (node == null) { res.status(404).json(JsonResponses.error("class not found: " + className)); return; }
        JvmClassInfo cls = (JvmClassInfo) node.getValue();

        CompletableFuture<DecompileResult> future;
        if (decompiler != null && !decompiler.isEmpty()) {
            JvmDecompiler d = dm.getJvmDecompiler(decompiler);
            if (d == null) {
                res.status(404).json(JsonResponses.error("unknown decompiler: " + decompiler));
                return;
            }
            future = dm.decompile(d, ws, cls);
        } else {
            future = dm.decompile(ws, cls);
        }

        DecompileResult result = future.get(60, TimeUnit.SECONDS);
        JsonObject out = new JsonObject();
        out.addProperty("class_name", className);
        out.addProperty("decompiler", decompiler == null || decompiler.isEmpty() ? dm.getTargetJvmDecompiler().getName() : decompiler);
        out.addProperty("text", result.getText());
        if (result.getException() != null) {
            out.addProperty("warning", result.getException().toString());
        }
        res.json(out);
    }
}
