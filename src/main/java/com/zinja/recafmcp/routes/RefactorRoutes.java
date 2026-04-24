package com.zinja.recafmcp.routes;

import com.google.gson.JsonObject;
import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import software.coley.recaf.services.inheritance.InheritanceGraph;
import software.coley.recaf.services.inheritance.InheritanceGraphService;
import software.coley.recaf.services.inheritance.InheritanceVertex;
import software.coley.recaf.services.mapping.IntermediateMappings;
import software.coley.recaf.services.mapping.MappingApplierService;
import software.coley.recaf.services.mapping.MappingResults;
import software.coley.recaf.services.mapping.format.MappingFileFormat;
import software.coley.recaf.services.mapping.format.MappingFormatManager;
import software.coley.recaf.services.workspace.WorkspaceManager;
import software.coley.recaf.workspace.model.Workspace;

import java.util.TreeSet;

public class RefactorRoutes {
    private final WorkspaceManager wm;
    private final MappingApplierService mappingApplierService;
    private final MappingFormatManager mappingFormatManager;
    private final InheritanceGraphService graphService;

    public RefactorRoutes(WorkspaceManager wm,
                          MappingApplierService mappingApplierService,
                          MappingFormatManager mappingFormatManager,
                          InheritanceGraphService graphService) {
        this.wm = wm;
        this.mappingApplierService = mappingApplierService;
        this.mappingFormatManager = mappingFormatManager;
        this.graphService = graphService;
    }

    public void register(McpHttpServer server) {
        server.post("/rename/class", (req, res) -> {
            Workspace ws = RouteSupport.requireWorkspace(wm, res);
            String className = RouteSupport.required(req.bodyString("class_name", ""), "class_name", res);
            String newName = RouteSupport.required(req.bodyString("new_name", ""), "new_name", res);
            if (ws == null || className == null || newName == null) return;
            if (RouteSupport.requireClass(ws, className, res) == null) return;
            respondApply(res, classMappings(className, newName), "class renamed");
        });

        server.post("/rename/method", (req, res) -> {
            Workspace ws = RouteSupport.requireWorkspace(wm, res);
            RouteSupport.MethodTarget target = RouteSupport.requireMethod(ws, req.bodyString("class_name", ""),
                    req.bodyString("method_name", ""), req.bodyString("descriptor", ""), res);
            String newName = RouteSupport.required(req.bodyString("new_name", ""), "new_name", res);
            if (target == null || newName == null) return;

            IntermediateMappings mappings = new IntermediateMappings();
            for (String owner : methodOwners(target, req.bodyBool("cascade_overrides", true))) {
                mappings.addMethod(owner, target.descriptor(), target.name(), newName);
            }
            respondApply(res, mappings, "method renamed");
        });

        server.post("/rename/field", (req, res) -> {
            Workspace ws = RouteSupport.requireWorkspace(wm, res);
            RouteSupport.FieldTarget target = RouteSupport.requireField(ws, req.bodyString("class_name", ""),
                    req.bodyString("field_name", ""), req.bodyString("descriptor", ""), res);
            String newName = RouteSupport.required(req.bodyString("new_name", ""), "new_name", res);
            if (target == null || newName == null) return;

            IntermediateMappings mappings = new IntermediateMappings();
            mappings.addField(target.owner(), target.descriptor(), target.name(), newName);
            respondApply(res, mappings, "field renamed");
        });

        server.post("/rename/package", (req, res) -> {
            Workspace ws = RouteSupport.requireWorkspace(wm, res);
            String oldPackage = RouteSupport.required(req.bodyString("old_package_name", ""), "old_package_name", res);
            if (ws == null || oldPackage == null) return;

            IntermediateMappings mappings = new IntermediateMappings();
            String oldPrefix = RefactorSupport.packagePrefix(oldPackage);
            String newPrefix = RefactorSupport.packagePrefix(req.bodyString("new_package_name", ""));
            RouteSupport.primaryBundles(ws.getPrimaryResource())
                    .flatMap(bundle -> bundle.values().stream())
                    .map(software.coley.recaf.info.JvmClassInfo::getName)
                    .filter(name -> name.equals(oldPrefix) || name.startsWith(oldPrefix + "/"))
                    .forEach(name -> mappings.addClass(name, RefactorSupport.remapPackage(name, oldPrefix, newPrefix)));

            if (mappings.isEmpty()) {
                res.status(404).json(JsonResponses.error("no classes matched package: " + oldPackage));
                return;
            }
            respondApply(res, mappings, "package renamed");
        });

        server.post("/rename/local-variable", (req, res) -> {
            Workspace ws = RouteSupport.requireWorkspace(wm, res);
            RouteSupport.MethodTarget target = RouteSupport.requireMethod(ws, req.bodyString("class_name", ""),
                    req.bodyString("method_name", ""), req.bodyString("descriptor", ""), res);
            String variableName = RouteSupport.required(req.bodyString("variable_name", ""), "variable_name", res);
            String newName = RouteSupport.required(req.bodyString("new_name", ""), "new_name", res);
            if (target == null || variableName == null || newName == null) return;

            int renamed = RefactorSupport.renameLocalVariables(ws, target, variableName, newName, req.bodyInt("index", -1));
            if (renamed == 0) {
                res.status(404).json(JsonResponses.error("local variable not found"));
                return;
            }

            JsonObject out = JsonResponses.ok("local variable renamed");
            out.addProperty("affected_classes", 1);
            out.addProperty("renamed_variables", renamed);
            res.json(out);
        });

        server.post("/rename/apply-mappings", (req, res) -> {
            Workspace ws = RouteSupport.requireWorkspace(wm, res);
            String mappingsText = RouteSupport.required(req.bodyString("mappings", ""), "mappings", res);
            if (ws == null || mappingsText == null) return;

            MappingFileFormat format = RefactorSupport.resolveFormat(mappingFormatManager, req.bodyString("format", "tiny-v2"));
            if (format == null) {
                res.status(404).json(JsonResponses.error("unknown mappings format"));
                return;
            }

            IntermediateMappings mappings = format.parse(mappingsText);
            if (mappings.isEmpty()) {
                res.status(400).json(JsonResponses.error("no changes to apply"));
                return;
            }

            JsonObject out = applyMappings(mappings, "mappings applied");
            out.addProperty("format", format.implementationName());
            res.json(out);
        });
    }

    private void respondApply(com.zinja.recafmcp.http.Response res, IntermediateMappings mappings, String message) throws Exception {
        if (mappings.isEmpty()) {
            res.status(400).json(JsonResponses.error("no changes to apply"));
            return;
        }
        res.json(applyMappings(mappings, message));
    }

    private JsonObject applyMappings(IntermediateMappings mappings, String message) {
        MappingResults results = mappingApplierService.inCurrentWorkspace().applyToPrimaryResource(mappings);
        results.apply();
        JsonObject out = JsonResponses.ok(message);
        out.addProperty("affected_classes", results.getPostMappingPaths().size());
        return out;
    }

    private IntermediateMappings classMappings(String className, String newName) {
        IntermediateMappings mappings = new IntermediateMappings();
        mappings.addClass(RouteSupport.internal(className), RouteSupport.internal(newName));
        return mappings;
    }

    private TreeSet<String> methodOwners(RouteSupport.MethodTarget target, boolean cascade) {
        TreeSet<String> owners = new TreeSet<>();
        owners.add(target.owner());
        if (!cascade) return owners;

        InheritanceGraph graph = graphService.getCurrentWorkspaceInheritanceGraph();
        if (graph == null) return owners;
        InheritanceVertex vertex = graph.getVertex(target.owner());
        if (vertex == null) return owners;

        vertex.getAllParents().stream()
                .filter(parent -> parent.hasMethod(target.name(), target.descriptor()))
                .map(InheritanceVertex::getName)
                .forEach(owners::add);
        vertex.getAllChildren().stream()
                .filter(child -> child.hasMethod(target.name(), target.descriptor()))
                .map(InheritanceVertex::getName)
                .forEach(owners::add);
        return owners;
    }

}
