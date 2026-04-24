package com.zinja.recafmcp.routes;

import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import software.coley.recaf.services.workspace.WorkspaceManager;

/**
 * Cross-reference endpoints.
 *
 * Recaf's {@code SearchService} has {@code MemberReferenceSearchQuery} (and
 * sibling queries) that produce exactly the data the Python xrefs tools want
 * — owner class, member, call-site offset, instruction opcode. The scaffold
 * leaves each endpoint as a 501 stub with a pointer to the right Recaf API to
 * avoid shipping a half-correct implementation.
 *
 * Implementation sketch for get_xrefs_to_method:
 *
 *   MemberReferenceSearchQuery q = new MemberReferenceSearchQuery(
 *           StringPredicate.equal(ownerInternal),
 *           StringPredicate.equal(methodName),
 *           StringPredicate.equal(descriptor));
 *   Results results = searchService.search(workspace, q);
 *   results.stream().forEach(result -> { ... serialize ... });
 *
 * Similar for fields (swap the query type) and classes (ClassReferenceSearchQuery).
 * Callees/overrides walk the inheritance graph — see InheritanceRoutes.
 */
public class XrefsRoutes {
    private final WorkspaceManager wm;

    public XrefsRoutes(WorkspaceManager wm) {
        this.wm = wm;
    }

    public void register(McpHttpServer server) {
        server.get("/xrefs-to-class", (req, res) -> res.status(501)
                .json(JsonResponses.error("xrefs-to-class not yet wired — use SearchService + ClassReferenceSearchQuery")));
        server.get("/xrefs-to-method", (req, res) -> res.status(501)
                .json(JsonResponses.error("xrefs-to-method not yet wired — use SearchService + MemberReferenceSearchQuery")));
        server.get("/xrefs-to-field", (req, res) -> res.status(501)
                .json(JsonResponses.error("xrefs-to-field not yet wired — use SearchService + MemberReferenceSearchQuery")));
        server.get("/callees-of-method", (req, res) -> res.status(501)
                .json(JsonResponses.error("callees-of-method not yet wired — walk method insns for INVOKE* opcodes")));
        server.get("/overrides-of-method", (req, res) -> res.status(501)
                .json(JsonResponses.error("overrides-of-method not yet wired — walk InheritanceGraph downwards")));

        // Silence unused-field warning until these are wired.
        Object unused = wm;
    }
}
