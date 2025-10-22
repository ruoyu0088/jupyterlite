"use strict";
(self.webpackChunkjupyterlab_open_url_parameter = self.webpackChunkjupyterlab_open_url_parameter || []).push([
    [568], {
        568: (e, t, a) => {
            a.r(t), a.d(t, {
                default: () => c
            });
            var r = a(247),
                o = a(162),
                n = a(261),
                s = a(226),
                l = a(186);
            const u = new RegExp("/(lab|notebooks|edit)/?"),
                c = {
                    id: "jupyterlab-open-url-parameter:plugin",
                    autoStart: !0,
                    requires: [r.IRouter, l.ITranslator],
                    optional: [s.IDefaultFileBrowser],
                    activate: (e, t, a, r) => {
                        var s;
                        const {
                            commands: c
                        } = e, i = null !== (s = a.load("jupyterlab")) && void 0 !== s ? s : l.nullTranslator, p = "router:fromUrl";
                        c.addCommand(p, {
                            execute: async a => {
                                var s;
                                const l = a,
                                    {
                                        request: p,
                                        search: d
                                    } = l,
                                    m = null !== (s = p.match(u)) && void 0 !== s ? s : [];
                                if (!m) return;
                                const h = new URLSearchParams(d),
                                    g = "fromURL",
                                    f = h.getAll(g);
                                if (!f || 0 === f.length) return;
                                const w = f.map((e => decodeURIComponent(e))),
                                    v = () => {
                                        const e = new URL(n.URLExt.join(n.PageConfig.getBaseUrl(), p));
                                        e.searchParams.delete(g);
                                        const {
                                            pathname: a,
                                            search: r
                                        } = e;
                                        t.navigate(`${a}${r}`, {
                                            skipRouting: !0
                                        })
                                    },
                                    b = async e => {
                                        var t;
                                        let a, s = "", filename = "";

                                        try {
                                            if (e.startsWith("data:")) {
                                                // Example: data:text/plain;name=hello.txt;base64,SGVsbG8gV29ybGQ=
                                                const [meta, dataPart] = e.split(",", 2);
                                                const parts = meta.split(";");

                                                // MIME type (after "data:")
                                                const mime = parts[0].slice(5) || "application/octet-stream";
                                                s = mime;

                                                // Optional filename (name=...)
                                                const namePart = parts.find(p => p.startsWith("name="));
                                                filename = namePart ? namePart.slice(5) : "untitled.txt";

                                                // Base64 or plain data?
                                                const isBase64 = parts.includes("base64");
                                                const content = isBase64
                                                    ? atob(dataPart)
                                                    : decodeURIComponent(dataPart);

                                                // Convert string to a Blob
                                                const u8 = new Uint8Array(content.length);
                                                for (let i = 0; i < content.length; i++) {
                                                    u8[i] = content.charCodeAt(i);
                                                }
                                                a = new Blob([u8], { type: mime });
                                            } else {
                                                // Normal URL
                                                const r = await fetch(e);
                                                a = await r.blob();
                                                s = (r.headers.get("Content-Type")) ?? "";
                                                filename = n.PathExt.basename(e);
                                            }
                                        } catch (err) {
                                            const reason = err;
                                            if (reason.response && reason.response.status !== 200) {
                                                reason.message = i.__("Could not open URL: %1", e);
                                            }
                                            return o.showErrorMessage(i.__("Cannot fetch"), reason);
                                        }

                                        // Upload and open
                                        try {
                                            const file = new File([a], filename, { type: s });
                                            const model = await (r?.model.upload(file));
                                            if (!model) return;
                                            return c.execute("docmanager:open", {
                                                path: model.path,
                                                options: { ref: "_noref" }
                                            });
                                        } catch (err) {
                                            return o.showErrorMessage(i._p("showErrorMessage", "Upload Error"), err);
                                        }
                                    }
                                    , [_] = m;
                                if ((null == _ ? void 0 : _.includes("/notebooks")) || (null == _ ? void 0 : _.includes("/edit"))) {
                                    const [e] = w;
                                    return await b(e), void v()
                                }
                                e.restored.then((async () => {
                                    await Promise.all(w.map((e => b(e)))), v()
                                }))
                            }
                        }), t.register({
                            command: p,
                            pattern: u
                        })
                    }
                }
        }
    }
]);