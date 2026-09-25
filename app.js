// 구글 드라이브 공유 링크(또는 파일 ID)에서 파일 ID를 뽑아낸다.
// 지원 형식: /file/d/ID/..., ?id=ID
function driveId(url) {
  if (!url || !/drive\.google\.com/.test(url)) return null;
  const m = url.match(/\/file\/d\/([\w-]+)/) || url.match(/[?&]id=([\w-]+)/);
  return m ? m[1] : null;
}

const $ = (id) => document.getElementById(id);
function el(tag, props, ...children) {
  const n = Object.assign(document.createElement(tag), props);
  n.append(...children);
  return n;
}

// 시청 완료 체크는 방문자 브라우저에만 저장된다 (저장이 막혀 있어도 페이지는 동작)
function loadDone() {
  try { return new Set(JSON.parse(localStorage.getItem("done") || "[]")); } catch { return new Set(); }
}
function saveDone(done) {
  try { localStorage.setItem("done", JSON.stringify([...done])); } catch {}
}

let posts = [];
const done = loadDone();

// 주소(#)로 화면을 바꾼다: # = 목록, #3 = 3번째 글
function route() {
  const n = Number(location.hash.slice(1));
  if (n >= 1 && n <= posts.length) showPost(n); else showList();
}

function showList() {
  $("list").hidden = false;
  $("post").hidden = true;
  $("post-body").replaceChildren(); // 목록으로 돌아오면 재생 중인 영상을 멈춘다
  $("back").hidden = true;
  $("done").hidden = true;

  $("list").replaceChildren(...posts.map((p, i) => {
    const videos = p.items.filter((it) => driveId(it.url)).length;
    return el("li", {}, el("a", { href: `#${i + 1}` },
      el("span", { className: "n" }, String(i + 1)),
      el("span", { className: "t" }, p.title),
      done.has(p.title)
        ? el("span", { className: "v ok" }, "✓ 완료")
        : el("span", { className: "v" }, videos ? `▶ ${videos}` : "")));
  }));
}

function showPost(n) {
  const p = posts[n - 1];
  $("list").hidden = true;
  $("post").hidden = false;
  $("back").hidden = false;
  $("done").hidden = false;
  $("done").setAttribute("aria-pressed", String(done.has(p.title)));
  $("post-title").textContent = p.title;

  $("post-body").replaceChildren(...p.items.map((it) => {
    const box = el("div", { className: "item" });
    if (it.text) box.append(el("p", {}, it.text));
    const id = driveId(it.url);
    if (id) {
      box.append(
        el("div", { className: "frame" }, el("iframe", {
          src: `https://drive.google.com/file/d/${id}/preview`,
          title: it.text || p.title, allow: "autoplay; fullscreen", allowFullscreen: true,
        })),
        el("a", { className: "open", href: `https://drive.google.com/file/d/${id}/view`, target: "_blank", rel: "noopener" },
          "영상이 안 보이면 구글 드라이브에서 열기 ↗"));
    } else if (it.url) {
      box.append(el("a", { className: "url", href: it.url, target: "_blank", rel: "noopener" }, it.url));
    }
    return box;
  }));

  const nav = (a, m) => {
    const ok = m >= 1 && m <= posts.length;
    a.href = ok ? `#${m}` : "#";
    a.setAttribute("aria-disabled", String(!ok));
  };
  nav($("prev"), n - 1);
  nav($("next"), n + 1);
  window.scrollTo(0, 0);
}

async function main() {
  try {
    const res = await fetch("videos.json", { cache: "no-cache" });
    const data = await res.json();
    posts = data.posts || [];
    if (data.board) {
      $("board").textContent = data.board;
      document.title = data.board;
    }
  } catch (e) {
    $("error").hidden = false;
    $("error").textContent = "videos.json을 불러오지 못했습니다. 웹 서버로 열었는지 확인하세요.";
    return;
  }

  $("done").addEventListener("click", () => {
    const p = posts[Number(location.hash.slice(1)) - 1];
    if (!p) return;
    if (done.has(p.title)) done.delete(p.title); else done.add(p.title);
    saveDone(done);
    $("done").setAttribute("aria-pressed", String(done.has(p.title)));
  });
  window.addEventListener("hashchange", route);
  route();
}

main();
