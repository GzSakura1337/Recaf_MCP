package com.zinja.recafmcp.routes;

import com.google.gson.JsonObject;
import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import software.coley.recaf.info.FileInfo;
import software.coley.recaf.path.FilePathNode;
import software.coley.recaf.services.workspace.WorkspaceManager;
import software.coley.recaf.workspace.model.Workspace;

import java.util.Base64;
import java.util.List;
import java.util.stream.Collectors;

public class FilesRoutes {
    private final WorkspaceManager wm;

    public FilesRoutes(WorkspaceManager wm) {
        this.wm = wm;
    }

    public void register(McpHttpServer server) {
        server.get("/files/list", (req, res) -> {
            Workspace ws = wm.getCurrent();
            if (ws == null) { res.json(JsonResponses.error("no workspace open")); return; }
            int offset = req.queryInt("offset", 0);
            int limit = req.queryInt("limit", 0);

            List<String> names = ws.filesStream()
                    .map(FilePathNode::getValue)
                    .map(FileInfo::getName)
                    .sorted()
                    .collect(Collectors.toList());

            JsonObject out = JsonResponses.paginated(names, "files", offset, limit,
                    n -> { JsonObject o = new JsonObject(); o.addProperty("path", (String) n); return o; });
            res.json(out);
        });

        server.get("/files/content", (req, res) -> {
            Workspace ws = wm.getCurrent();
            if (ws == null) { res.json(JsonResponses.error("no workspace open")); return; }
            String path = req.query("path");
            if (path == null || path.isEmpty()) {
                res.status(400).json(JsonResponses.error("missing 'path'"));
                return;
            }
            FilePathNode node = ws.findFile(path);
            if (node == null) { res.status(404).json(JsonResponses.error("file not found")); return; }
            FileInfo file = node.getValue();
            byte[] bytes = file.getRawContent();

            JsonObject out = new JsonObject();
            out.addProperty("path", file.getName());
            out.addProperty("size", bytes.length);

            // Heuristic: if we can decode as UTF-8 without replacement chars,
            // treat it as text; otherwise base64.
            String asText = tryDecodeUtf8(bytes);
            if (asText != null) {
                out.addProperty("encoding", "utf-8");
                out.addProperty("content", asText);
            } else {
                out.addProperty("encoding", "base64");
                out.addProperty("content", Base64.getEncoder().encodeToString(bytes));
            }
            res.json(out);
        });

        server.get("/files/manifest", (req, res) -> {
            Workspace ws = wm.getCurrent();
            if (ws == null) { res.json(JsonResponses.error("no workspace open")); return; }
            FilePathNode node = ws.findFile("META-INF/MANIFEST.MF");
            if (node == null) { res.json(JsonResponses.error("no MANIFEST.MF")); return; }
            JsonObject out = new JsonObject();
            out.addProperty("path", "META-INF/MANIFEST.MF");
            out.addProperty("content", new String(node.getValue().getRawContent(), java.nio.charset.StandardCharsets.UTF_8));
            res.json(out);
        });

        server.get("/files/strings", (req, res) -> {
            // TODO: scan non-class files for printable strings. For a first cut
            // this returns only the per-class constant-pool strings.
            res.status(501).json(JsonResponses.error("strings-from-resources not yet implemented"));
        });
    }

    private static String tryDecodeUtf8(byte[] bytes) {
        try {
            java.nio.charset.CharsetDecoder dec = java.nio.charset.StandardCharsets.UTF_8
                    .newDecoder()
                    .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
                    .onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT);
            return dec.decode(java.nio.ByteBuffer.wrap(bytes)).toString();
        } catch (Exception e) {
            return null;
        }
    }
}
