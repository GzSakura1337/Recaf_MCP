package com.zinja.recafmcp.routes;

import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import software.coley.recaf.services.mapping.MappingApplierService;
import software.coley.recaf.services.workspace.WorkspaceManager;

/**
 * Refactor endpoints — all go through {@link MappingApplierService}.
 *
 * Implementation sketch for rename_class:
 *
 *   IntermediateMappings mappings = new IntermediateMappings();
 *   mappings.addClass(oldInternal, newInternal);
 *   MappingResults results = mappingApplierService.inCurrentWorkspace().applyToPrimaryResource(mappings);
 *   results.apply();                 // commits the rename into the workspace
 *   return results.getPostMappingPaths().size();  // number of affected classes
 *
 * rename_method / rename_field follow the same pattern with
 * {@code mappings.addMethod(owner, desc, name, newName)} and
 * {@code mappings.addField(owner, desc, name, newName)}.
 *
 * rename_package is a loop over every class under {@code old/} that rewrites
 * the prefix. apply_mappings parses the file first with the matching
 * MappingFileFormat (ProguardMappings / TinyV2Mappings / ...), then feeds the
 * result into MappingApplierService.
 */
public class RefactorRoutes {
    private final WorkspaceManager wm;
    private final MappingApplierService mappingApplierService;

    public RefactorRoutes(WorkspaceManager wm, MappingApplierService mappingApplierService) {
        this.wm = wm;
        this.mappingApplierService = mappingApplierService;
    }

    public void register(McpHttpServer server) {
        server.post("/rename/class", (req, res) -> res.status(501)
                .json(JsonResponses.error("rename_class not yet wired — use IntermediateMappings.addClass + MappingApplier")));
        server.post("/rename/method", (req, res) -> res.status(501)
                .json(JsonResponses.error("rename_method not yet wired — use IntermediateMappings.addMethod")));
        server.post("/rename/field", (req, res) -> res.status(501)
                .json(JsonResponses.error("rename_field not yet wired — use IntermediateMappings.addField")));
        server.post("/rename/package", (req, res) -> res.status(501)
                .json(JsonResponses.error("rename_package not yet wired — loop classes and rewrite prefix via MappingApplier")));
        server.post("/rename/local-variable", (req, res) -> res.status(501)
                .json(JsonResponses.error("rename_local_variable not yet wired — patch LocalVariableTable and reinsert class")));
        server.post("/rename/apply-mappings", (req, res) -> res.status(501)
                .json(JsonResponses.error("apply_mappings not yet wired — parse with MappingFormatManager then apply")));

        Object unused1 = wm;
        Object unused2 = mappingApplierService;
    }
}
