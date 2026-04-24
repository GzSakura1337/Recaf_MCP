package com.zinja.recafmcp.routes;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.zinja.recafmcp.http.JsonResponses;
import com.zinja.recafmcp.http.McpHttpServer;
import software.coley.recaf.info.ClassInfo;
import software.coley.recaf.info.JvmClassInfo;
import software.coley.recaf.info.member.FieldMember;
import software.coley.recaf.info.member.MethodMember;
import software.coley.recaf.path.ClassPathNode;
import software.coley.recaf.services.search.SearchService;
import software.coley.recaf.services.workspace.WorkspaceManager;
import software.coley.recaf.workspace.model.Workspace;

import java.util.regex.Pattern;
import java.util.stream.Stream;

/**
 * Search endpoints.
 *
 * The methods below implement name/member/string searches by streaming the
 * workspace directly — good enough for an initial scaffold. For richer queries
 * (instructions, numeric constants, scoped queries) switch to
 * {@link SearchService}: it exposes {@code search(Workspace, AbstractSearchQuery)}
 * and visitor-based result collection, which is what the Recaf UI uses.
 *
 * TODO: port these handlers onto SearchService once the exact query builders
 *       (StringSearchQuery, MemberReferenceSearchQuery, ...) are wired in.
 */
public class SearchRoutes {
    private final WorkspaceManager wm;
    @SuppressWarnings("unused")
    private final SearchService searchService;

    public SearchRoutes(WorkspaceManager wm, SearchService searchService) {
        this.wm = wm;
        this.searchService = searchService;
    }

    public void register(McpHttpServer server) {
        server.get("/search/classes", (req, res) -> {
            Workspace ws = wm.getCurrent();
            if (ws == null) { res.json(JsonResponses.error("no workspace open")); return; }
            Matcher matcher = Matcher.of(req.query("pattern", ""),
                    req.queryBool("regex", false),
                    req.queryBool("case_sensitive", true));

            JsonArray hits = new JsonArray();
            ws.jvmClassesStream()
                    .map(ClassPathNode::getValue)
                    .map(ClassInfo::getName)
                    .filter(n -> matcher.matches(n.replace('/', '.')))
                    .sorted()
                    .forEach(n -> {
                        JsonObject o = new JsonObject();
                        o.addProperty("name", n.replace('/', '.'));
                        hits.add(o);
                    });
            JsonObject out = new JsonObject();
            out.add("classes", hits);
            res.json(out);
        });

        server.get("/search/members", (req, res) -> {
            Workspace ws = wm.getCurrent();
            if (ws == null) { res.json(JsonResponses.error("no workspace open")); return; }
            Matcher matcher = Matcher.of(req.query("pattern", ""),
                    req.queryBool("regex", false),
                    req.queryBool("case_sensitive", true));
            String kind = req.query("kind", "any");

            JsonArray hits = new JsonArray();
            ws.jvmClassesStream().forEach(node -> {
                JvmClassInfo cls = (JvmClassInfo) node.getValue();
                if (kind.equals("any") || kind.equals("method")) {
                    for (MethodMember m : cls.getMethods()) {
                        if (matcher.matches(m.getName())) {
                            JsonObject o = new JsonObject();
                            o.addProperty("kind", "method");
                            o.addProperty("owner", cls.getName().replace('/', '.'));
                            o.addProperty("name", m.getName());
                            o.addProperty("descriptor", m.getDescriptor());
                            hits.add(o);
                        }
                    }
                }
                if (kind.equals("any") || kind.equals("field")) {
                    for (FieldMember f : cls.getFields()) {
                        if (matcher.matches(f.getName())) {
                            JsonObject o = new JsonObject();
                            o.addProperty("kind", "field");
                            o.addProperty("owner", cls.getName().replace('/', '.'));
                            o.addProperty("name", f.getName());
                            o.addProperty("descriptor", f.getDescriptor());
                            hits.add(o);
                        }
                    }
                }
            });
            JsonObject out = new JsonObject();
            out.add("members", hits);
            res.json(out);
        });

        server.get("/search/strings", (req, res) -> {
            Workspace ws = wm.getCurrent();
            if (ws == null) { res.json(JsonResponses.error("no workspace open")); return; }
            Matcher matcher = Matcher.of(req.query("pattern", ""),
                    req.queryBool("regex", false),
                    req.queryBool("case_sensitive", true));

            JsonArray hits = new JsonArray();
            ws.jvmClassesStream().forEach(node -> {
                JvmClassInfo cls = (JvmClassInfo) node.getValue();
                for (String s : cls.getStringConstants()) {
                    if (matcher.matches(s)) {
                        JsonObject o = new JsonObject();
                        o.addProperty("owner", cls.getName().replace('/', '.'));
                        o.addProperty("value", s);
                        hits.add(o);
                    }
                }
            });
            JsonObject out = new JsonObject();
            out.add("hits", hits);
            res.json(out);
        });

        server.get("/search/numbers", (req, res) -> {
            // TODO: implement via SearchService.search(ws, new NumberSearchQuery(value))
            //       or by streaming method insns and matching LdcInsnNode operands.
            res.status(501).json(JsonResponses.error("numeric-constant search not yet wired"));
        });

        server.get("/search/instructions", (req, res) -> {
            // TODO: implement via SearchService or ClassReader visitor that filters
            //       on opcode mnemonic + operand substring.
            res.status(501).json(JsonResponses.error("instruction search not yet wired"));
        });
    }

    /** Tiny text matcher supporting regex / case-insensitive / substring modes. */
    private static final class Matcher {
        private final Pattern pattern;
        private final String needle;
        private final boolean caseSensitive;

        private Matcher(Pattern pattern, String needle, boolean caseSensitive) {
            this.pattern = pattern;
            this.needle = needle;
            this.caseSensitive = caseSensitive;
        }

        static Matcher of(String text, boolean regex, boolean caseSensitive) {
            if (regex) {
                int flags = caseSensitive ? 0 : Pattern.CASE_INSENSITIVE;
                return new Matcher(Pattern.compile(text, flags), null, caseSensitive);
            }
            return new Matcher(null, caseSensitive ? text : text.toLowerCase(), caseSensitive);
        }

        boolean matches(String input) {
            if (input == null) return false;
            if (pattern != null) return pattern.matcher(input).find();
            String s = caseSensitive ? input : input.toLowerCase();
            return s.contains(needle);
        }
    }
}
