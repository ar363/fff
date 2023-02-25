const root = document.getElementById("infroot");

const hydrated = JSON.parse(document.getElementById("HYDRATE").innerText);

let pageAt = 0;

for (pageAt = 1; pageAt <= hydrated.book.total_pages; pageAt++) {
  root.innerHTML += /*html*/ `
    <a href="/book_cap/${hydrated.book.id}/${pageAt}" target="_blank"><img src="/api/imprev/${hydrated.book.id}/${pageAt}/"></a>
    `;
}
