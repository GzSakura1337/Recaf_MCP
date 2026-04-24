package com.zinja.recafmcp.routes;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import com.zinja.recafmcp.state.UiState;
import software.coley.recaf.services.workspace.WorkspaceManager;
import software.coley.recaf.workspace.model.Workspace;
import software.coley.recaf.workspace.model.resource.WorkspaceResource;

public class WorkspaceRoutes {
    private final WorkspaceManager wm;
    private final UiState uiState;

    public WorkspaceRoutes(WorkspaceManager wm, UiState uiState) {
        this.wm = wm;
        this.uiState = uiState;
    }

    public void register(McpHttpServer server) {
        server.get("/workspace/info", (req, res) -> {
            Workspace ws = wm.getCurrent();
            if (ws == null) {
                res.json(JsonResponses.error("no workspace open"));
                return;
            }
            JsonObject out = new JsonObject();
            out.addProperty("has_workspace", true);
            out.add("primary", resourceSummary(ws.getPrimaryResource()));
            JsonArray supporting = new JsonArray();
            for (WorkspaceResource r : ws.getSupportingResources()) supporting.add(resourceSummary(r));
            out.add("supporting", supporting);
            res.json(out);
        });

        server.get("/workspace/supporting", (req, res) -> {
            Workspace ws = requireWorkspace(res);
            if (ws == null) return;
            JsonArray arr = new JsonArray();
            for (WorkspaceResource r : ws.getSupportingResources()) arr.add(resourceSummary(r));
            JsonObject out = new JsonObject();
            out.add("resources", arr);
            res.json(out);
        });

        server.post("/workspace/close", (req, res) -> {
            boolean closed = wm.closeCurrent();
            res.json(closed ? JsonResponses.ok("workspace closed") : JsonResponses.error("failed to close workspace"));
        });

        server.post("/workspace/open", (req, res) -> {
            // TODO: implement using ResourceImporter.
            //
            //   @Inject ResourceImporter importer; // software.coley.recaf.services.workspace.io.ResourceImporter
            //   WorkspaceResource resource = importer.importResource(Paths.get(path));
            //   Workspace ws = new BasicWorkspace(resource);
            //   wm.setCurrent(ws);
            //
            // The importer auto-detects jar / war / class / directory.
            String path = req.bodyString("path", "");
            if (path.isEmpty()) {
                res.status(400).json(JsonResponses.error("missing 'path'"));
                return;
            }
            res.status(501).json(JsonResponses.error("open_workspace not yet wired — inject ResourceImporter and call importer.importResource(Paths.get(path))"));
        });

        server.post("/workspace/add-supporting", (req, res) -> {
            // TODO: same importer flow, then workspace.addSupportingResource(resource).
            res.status(501).json(JsonResponses.error("add_supporting_resource not yet wired"));
        });

        server.get("/current-class", (req, res) -> {
            String name = uiState.getCurrentClassName();
            JsonObject out = new JsonObject();
            out.addProperty("class_name", name);
            if (name != null) {
                Workspace ws = wm.getCurrent();
                if (ws != null && ws.findJvmClass(name) != null) {
                    out.addProperty("found", true);
                }
            }
            res.json(out);
        });

        server.get("/selected-text", (req, res) -> {
            JsonObject out = new JsonObject();
            out.addProperty("text", uiState.getSelectedText());
            res.json(out);
        });
    }

    private Workspace requireWorkspace(com.zinja.recafmcp.http.Response res) throws Exception {
        Workspace ws = wm.getCurrent();
        if (ws == null) {
            res.status(409).json(JsonResponses.error("no workspace open"));
            return null;
        }
        return ws;
    }

    private static JsonObject resourceSummary(WorkspaceResource resource) {
        JsonObject obj = new JsonObject();
        if (resource == null) return obj;
        // Best-effort summary; richer metadata (path, jar version) depends on the
        // concrete WorkspaceResource subtype and can be added later.
        obj.addProperty("type", resource.getClass().getSimpleName());
        obj.addProperty("class_count", (int) resource.jvmClassBundleStream()
                .mapToLong(b -> b.values().size()).sum());
        obj.addProperty("file_count", (int) resource.fileBundleStream()
                .mapToLong(b -> b.values().size()).sum());
        return obj;
    }
}
