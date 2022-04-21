"use strict";

////////////////////////////////////////////////////////////////
// The first time the page loads set title and state
window.addEventListener("DOMContentLoaded", () => {
  const main_content = document.querySelector(".content");

  // set the state for the first loaded page
  const url = main_content.dataset.url;
  history.replaceState({ url: url }, "", url);

  // set title
  document.title = main_content.dataset.title;
});

////////////////////////////////////////////////////////////////
// spa - fetch and show content
const spa = async (url, replace_state = true, event = null) => {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  // fetch the html content
  let conn = await fetch(url, { headers: { spa: "yes" } });
  let html = await conn.text();

  // set the html to the content
  document.querySelector("body").innerHTML = html;

  // set state
  if (replace_state) {
    history.pushState({ url: conn.url }, "", conn.url);
    // scroll to top of page
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
  } else if (conn.redirected) {
    // if the connection has been redirected, call spa again to update to correct page
    // this happens when clicking the backbutton and landing on '/login' which, while logged in, will redirect to '/home'
    spa(conn.url, true);
  }

  // set title
  const main_content = document.querySelector(".content");
  const title = main_content.dataset.title;
  document.title = title;
};

////////////////////////////////////////////////////////////////
// handle clicking 'back' in the browsers
window.addEventListener("popstate", (event) => {
  event.preventDefault();
  event.stopPropagation();
  spa(event.state.url, false, event);
});
