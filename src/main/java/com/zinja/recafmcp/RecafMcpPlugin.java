package com.zinja.recafmcp;

import com.zinja.recafmcp.http.McpHttpServer;
import com.zinja.recafmcp.routes.ClassRoutes;
import com.zinja.recafmcp.routes.DecompileRoutes;
import com.zinja.recafmcp.routes.ExportRoutes;
import com.zinja.recafmcp.routes.FilesRoutes;
import com.zinja.recafmcp.routes.InheritanceRoutes;
import com.zinja.recafmcp.routes.MethodRoutes;
import com.zinja.recafmcp.routes.RefactorRoutes;
import com.zinja.recafmcp.routes.SearchRoutes;
import com.zinja.recafmcp.routes.WorkspaceRoutes;
import com.zinja.recafmcp.routes.XrefsRoutes;
import com.zinja.recafmcp.state.UiState;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import software.coley.recaf.plugin.Plugin;
import software.coley.recaf.plugin.PluginInformation;
import software.coley.recaf.services.decompile.DecompilerManager;
import software.coley.recaf.services.inheritance.InheritanceGraphService;
import software.coley.recaf.services.mapping.MappingApplierService;
import software.coley.recaf.services.search.SearchService;
import software.coley.recaf.services.workspace.WorkspaceManager;

import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Recaf 4 plugin entry point — exposes the services the Python MCP server needs
 * over a localhost HTTP API (default 127.0.0.1:8750).
 *
 * Port / host are controlled by system properties so the user can override at
 * launch:
 *   -Drecaf.mcp.host=127.0.0.1
 *   -Drecaf.mcp.port=8750
 */
@ApplicationScoped
@PluginInformation(
        id = "recaf-mcp-plugin",
        name = "Recaf MCP Plugin",
        version = "0.1.0",
        author = "zinja",
        description = "Exposes Recaf reverse-engineering operations over HTTP for the Recaf MCP server.",
        dependencies = {},
        softDependencies = {}
)
public class RecafMcpPlugin implements Plugin {
    private static final Logger LOG = Logger.getLogger(RecafMcpPlugin.class.getName());

    private static final String DEFAULT_HOST = "127.0.0.1";
    private static final int DEFAULT_PORT = 8750;

    private final WorkspaceManager workspaceManager;
    private final DecompilerManager decompilerManager;
    private final SearchService searchService;
    private final MappingApplierService mappingApplierService;
    private final InheritanceGraphService inheritanceGraphService;

    private McpHttpServer server;
    private UiState uiState;

    @Inject
    public RecafMcpPlugin(WorkspaceManager workspaceManager,
                          DecompilerManager decompilerManager,
                          SearchService searchService,
                          MappingApplierService mappingApplierService,
                          InheritanceGraphService inheritanceGraphService) {
        this.workspaceManager = workspaceManager;
        this.decompilerManager = decompilerManager;
        this.searchService = searchService;
        this.mappingApplierService = mappingApplierService;
        this.inheritanceGraphService = inheritanceGraphService;
    }

    @Override
    public void onEnable() {
        String host = System.getProperty("recaf.mcp.host", DEFAULT_HOST);
        int port = Integer.getInteger("recaf.mcp.port", DEFAULT_PORT);

        uiState = new UiState();
        uiState.install(workspaceManager);

        server = new McpHttpServer(host, port);

        // Health
        server.get("/health", (req, res) -> res.text("ok"));

        // Register domain routes.
        new WorkspaceRoutes(workspaceManager, uiState).register(server);
        new ClassRoutes(workspaceManager).register(server);
        new MethodRoutes(workspaceManager).register(server);
        new SearchRoutes(workspaceManager, searchService).register(server);
        new XrefsRoutes(workspaceManager).register(server);
        new RefactorRoutes(workspaceManager, mappingApplierService).register(server);
        new DecompileRoutes(workspaceManager, decompilerManager).register(server);
        new InheritanceRoutes(workspaceManager, inheritanceGraphService).register(server);
        new FilesRoutes(workspaceManager).register(server);
        new ExportRoutes(workspaceManager).register(server);

        try {
            server.start();
            LOG.info("Recaf MCP plugin listening on http://" + host + ":" + port);
        } catch (Exception e) {
            LOG.log(Level.SEVERE, "Failed to start Recaf MCP HTTP server", e);
        }
    }

    @Override
    public void onDisable() {
        if (server != null) {
            server.stop();
            server = null;
        }
        if (uiState != null) {
            uiState.uninstall(workspaceManager);
            uiState = null;
        }
    }
}
