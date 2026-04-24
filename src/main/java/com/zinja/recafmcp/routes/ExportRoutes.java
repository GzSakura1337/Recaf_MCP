package com.zinja.recafmcp.routes;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import software.coley.recaf.services.workspace.WorkspaceManager;
import software.coley.recaf.services.workspace.io.PathWorkspaceExportConsumer;
import software.coley.recaf.services.workspace.io.WorkspaceCompressType;
import software.coley.recaf.services.workspace.io.WorkspaceExportOptions;
import software.coley.recaf.services.workspace.io.WorkspaceOutputType;
import software.coley.recaf.workspace.model.Workspace;
import software.coley.recaf.workspace.model.bundle.JvmClassBundle;
import software.coley.recaf.workspace.model.resource.WorkspaceResource;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.TreeSet;
import java.util.stream.Stream;

public class ExportRoutes {
    private final WorkspaceManager wm;

    public ExportRoutes(WorkspaceManager wm) {
        this.wm = wm;
    }

    public void register(McpHttpServer server) {
        server.post("/export/workspace", (req, res) -> {
            Workspace ws = requireWorkspace(res);
            String outputPath = req.bodyString("output_path", "");
            if (ws == null) return;
            if (outputPath.isBlank()) {
                res.status(400).json(JsonResponses.error("missing 'output_path'"));
                return;
            }

            Path path = Paths.get(outputPath).toAbsolutePath().normalize();
            WorkspaceOutputType outputType = outputType(path);
            prepareOutput(path, outputType);

            WorkspaceExportOptions options = new WorkspaceExportOptions(
                    WorkspaceCompressType.MATCH_ORIGINAL,
                    outputType,
                    new PathWorkspaceExportConsumer(path));
            options.setBundleSupporting(req.bodyBool("include_supporting", false));
            options.create().export(ws);

            JsonObject out = JsonResponses.ok("workspace exported");
            out.addProperty("output_path", path.toString());
            out.addProperty("output_type", outputType.name().toLowerCase());
            res.json(out);
        });

        server.get("/export/modified-classes", (req, res) -> {
            Workspace ws = requireWorkspace(res);
            if (ws == null) return;

            TreeSet<String> names = new TreeSet<>();
            for (JvmClassBundle bundle : bundles(ws.getPrimaryResource()).toList()) {
                bundle.getDirtyKeys().stream()
                        .map(name -> name.replace('/', '.'))
                        .forEach(names::add);
            }

            JsonArray arr = new JsonArray();
            names.forEach(arr::add);
            JsonObject out = new JsonObject();
            out.add("modified_classes", arr);
            out.addProperty("count", names.size());
            res.json(out);
        });

        server.post("/export/revert-class", (req, res) -> {
            Workspace ws = requireWorkspace(res);
            String className = req.bodyString("class_name", "");
            if (ws == null) return;
            if (className.isBlank()) {
                res.status(400).json(JsonResponses.error("missing 'class_name'"));
                return;
            }

            String internalName = className.replace('.', '/');
            for (JvmClassBundle bundle : bundles(ws.getPrimaryResource()).toList()) {
                if (!bundle.containsKey(internalName)) continue;
                if (!bundle.getDirtyKeys().contains(internalName)) {
                    res.json(JsonResponses.ok("class is already clean"));
                    return;
                }

                int steps = 0;
                while (bundle.getDirtyKeys().contains(internalName) && bundle.hasHistory(internalName) && steps++ < 64) {
                    bundle.decrementHistory(internalName);
                }

                if (bundle.getDirtyKeys().contains(internalName)) {
                    res.status(409).json(JsonResponses.error("failed to fully revert class"));
                    return;
                }

                JsonObject out = JsonResponses.ok("class reverted");
                out.addProperty("class_name", className);
                res.json(out);
                return;
            }

            res.status(404).json(JsonResponses.error("class not found: " + className));
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

    private static Stream<JvmClassBundle> bundles(WorkspaceResource resource) {
        return Stream.concat(
                resource.jvmClassBundleStreamRecursive(),
                resource.versionedJvmClassBundleStreamRecursive().map(bundle -> (JvmClassBundle) bundle));
    }

    private static WorkspaceOutputType outputType(Path path) {
        if (Files.isDirectory(path)) return WorkspaceOutputType.DIRECTORY;
        String name = path.getFileName() == null ? "" : path.getFileName().toString();
        return name.contains(".") ? WorkspaceOutputType.FILE : WorkspaceOutputType.DIRECTORY;
    }

    private static void prepareOutput(Path path, WorkspaceOutputType outputType) throws Exception {
        if (outputType == WorkspaceOutputType.DIRECTORY) {
            Files.createDirectories(path);
            return;
        }

        Path parent = path.getParent();
        if (parent != null) Files.createDirectories(parent);
    }
}
