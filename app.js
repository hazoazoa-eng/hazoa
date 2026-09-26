// 링크가 동영상이면 페이지 안에 넣을 플레이어 주소를 돌려준다.
// 구글 드라이브: /file/d/ID/..., ?id=ID   유튜브: youtu.be/ID, watch?v=ID, /shorts/ID, /live/ID
function videoEmbed(url) {
  if (!url) return null;
  let m;
  if (/drive\.google\.com/.test(url) && (m = url.match(/\/file\/d\/([\w-]+)/) || url.match(/[?&]id=([\w-]+)/))) {
    return { src: `https://drive.google.com/file/d/${m[1]}/preview`, open: `https://drive.google.com/file/d/${m[1]}/view`, name: "구글 드라이브" };
  }
  if ((m = url.match(/youtu\.be\/([\w-]{11})/) || url.match(/youtube\.com\/(?:watch\?(?:.*&)?v=|shorts\/|live\/|embed\/)([\w-]{11})/))) {
    return { src: `https://www.youtube-nocookie.com/embed/${m[1]}`, open: `https://youtu.be/${m[1]}`, name: "유튜브" };
  }
  return null;
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

let posts = [];   // 모든 글을 한 줄로 편 것 (#번호는 이 순서)
let groups = [];  // [{ title, posts }] 논리 단계별 묶음
let loose = [];   // 묶음 없이 쓴 글 (예전 "posts" 형식)
let reading = null;
const openGroups = new Set();
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

  const row = (p) => {
    const i = posts.indexOf(p);
    const videos = p.items.filter((it) => videoEmbed(it.url)).length;
    return el("li", {}, el("a", { href: `#${i + 1}` },
      el("span", { className: "n" }, String(i + 1)),
      el("span", { className: "t" }, p.title),
      done.has(p.title)
        ? el("span", { className: "v ok" }, "✓ 완료")
        : el("span", { className: "v" }, videos ? `▶ ${videos}` : "")));
  };

  const rows = [];
  if (reading) {
    const t = reading.url
      ? el("a", { href: reading.url, target: "_blank", rel: "noopener" }, reading.title)
      : reading.title;
    rows.push(el("li", { className: "reading" }, t));
  }
  // 논리 단계(Logic 1, 2, …)는 눌러서 펼치는 묶음으로 보여 준다
  for (const g of groups) {
    const d = el("details", { open: openGroups.has(g.title) },
      el("summary", {}, g.title),
      el("ul", {}, ...g.posts.map(row)));
    d.addEventListener("toggle", () => {
      if (d.open) openGroups.add(g.title); else openGroups.delete(g.title);
    });
    rows.push(el("li", { className: "group" }, d));
  }
  rows.push(...loose.map(row));
  $("list").replaceChildren(...rows);
}

function showPost(n) {
  const p = posts[n - 1];
  // 목록으로 돌아왔을 때 이 글이 든 묶음이 펼쳐져 있도록
  const g = groups.find((g) => g.posts.includes(p));
  if (g) openGroups.add(g.title);
  $("list").hidden = true;
  $("post").hidden = false;
  $("back").hidden = false;
  $("done").hidden = false;
  $("done").setAttribute("aria-pressed", String(done.has(p.title)));
  $("post-title").textContent = p.title;

  $("post-body").replaceChildren(...p.items.map((it) => {
    const box = el("div", { className: "item" });
    if (it.text) box.append(el("p", {}, it.text));
    const video = videoEmbed(it.url);
    if (video) {
      box.append(
        el("div", { className: "frame" }, el("iframe", {
          src: video.src, title: it.text || p.title,
          allow: "autoplay; fullscreen; picture-in-picture", allowFullscreen: true,
        })),
        el("a", { className: "open", href: video.open, target: "_blank", rel: "noopener" },
          `영상이 안 보이면 ${video.name}에서 열기 ↗`));
    } else if (it.video) {
      box.append(el("div", { className: "frame pending" }, "영상 준비 중"));
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
    groups = data.groups || [];
    loose = data.posts || [];
    reading = data.reading || null;
    posts = [...groups.flatMap((g) => g.posts), ...loose];
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
