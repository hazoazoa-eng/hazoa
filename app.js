// 구글 드라이브 공유 링크(또는 파일 ID)에서 파일 ID를 뽑아낸다.
// 지원 형식: /file/d/ID/..., ?id=ID, 파일 ID 단독
function driveId(url) {
  const m = url.match(/\/file\/d\/([\w-]+)/) || url.match(/[?&]id=([\w-]+)/);
  if (m) return m[1];
  return /^[\w-]{10,}$/.test(url) ? url : null;
}

const previewUrl = (id) => `https://drive.google.com/file/d/${id}/preview`;
const viewUrl = (id) => `https://drive.google.com/file/d/${id}/view`;

function play(video, id, button) {
  document.getElementById("player").hidden = false;
  document.getElementById("player-frame").src = previewUrl(id);
  document.getElementById("player-title").textContent = video.title;
  document.getElementById("player-desc").textContent = video.description || "";
  document.getElementById("player-link").href = viewUrl(id);
  document.querySelectorAll(".list button").forEach((b) => b.removeAttribute("aria-current"));
  button.setAttribute("aria-current", "true");
  history.replaceState(null, "", `#${id}`);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function main() {
  const list = document.getElementById("list");
  const error = document.getElementById("error");
  let videos;
  try {
    const res = await fetch("videos.json", { cache: "no-cache" });
    videos = await res.json();
  } catch (e) {
    error.hidden = false;
    error.textContent = "videos.json을 불러오지 못했습니다. 웹 서버로 열었는지 확인하세요.";
    return;
  }

  const buttons = {};
  for (const video of videos) {
    const id = driveId(video.url);
    if (!id) continue;
    const li = document.createElement("li");
    const button = document.createElement("button");
    const title = document.createElement("strong");
    const desc = document.createElement("span");
    title.textContent = video.title;
    desc.textContent = video.description || "";
    button.append(title, desc);
    button.addEventListener("click", () => play(video, id, button));
    li.append(button);
    list.append(li);
    buttons[id] = [video, button];
  }

  if (!list.children.length) {
    error.hidden = false;
    error.textContent = "재생할 영상이 없습니다. videos.json에 구글 드라이브 공유 링크를 추가하세요.";
    return;
  }

  // 주소 끝에 #파일ID 가 있으면 그 영상을 바로 연다 (영상별 공유 링크용)
  const hash = location.hash.slice(1);
  if (buttons[hash]) play(buttons[hash][0], hash, buttons[hash][1]);
}

main();
