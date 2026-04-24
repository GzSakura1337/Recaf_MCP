package com.zinja.recafmcp.routes;

import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import software.coley.recaf.services.workspace.WorkspaceManager;

/**
 * Export endpoints.
 *
 * Implementation sketch for export_workspace:
 *
 *   @Inject WorkspaceExportOptions.Builder builder;
 *   WorkspaceExportOptions options = builder
 *           .setOutputType(OutputType.FILE)
 *           .setPath(Paths.get(outputPath))
 *           .build();
 *   options.create().export(workspace);
 *
 * (The exact factory lives in software.coley.recaf.services.workspace.io —
 * look for WorkspaceExporter / BasicWorkspaceExportOptions.)
 *
 * get_modified_classes walks every WorkspaceResource bundle and compares each
 * class's current bytes against its original bytes stamp (ClassBundle tracks a
 * history/dirty flag).
 */
public class ExportRoutes {
    private final WorkspaceManager wm;

    public ExportRoutes(WorkspaceManager wm) {
        this.wm = wm;
    }

    public void register(McpHttpServer server) {
        server.post("/export/workspace", (req, res) -> res.status(501)
                .json(JsonResponses.error("export-workspace not yet wired — use WorkspaceExportOptions + WorkspaceExporter")));
        server.get("/export/modified-classes", (req, res) -> res.status(501)
                .json(JsonResponses.error("modified-class tracking not yet wired")));
        server.post("/export/revert-class", (req, res) -> res.status(501)
                .json(JsonResponses.error("revert-class not yet wired — bundle.remove() + reinsert original bytes")));

        Object unused = wm;
    }
}
