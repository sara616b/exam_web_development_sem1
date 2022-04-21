"use strict";

const sign_up = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  const form = event.target.form;
  if (is_it_valid(form)) {
    await fetch("/signup", {
      method: "POST",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected) {
        // if it's been redirected there're errors sent with query string or it went through and will send the user to /home
        spa(response.url, true, event);
      } else {
        // get to login
        spa("/login", true, event);
      }
    });
  }
  set_button_status_default(event.target);
};

const log_in = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  const form = event.target.form;
  if (is_it_valid(form)) {
    await fetch("/login", {
      method: "PUT",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected) {
        // if it's been redirected there're errors send with query string
        spa(response.url, true, event);
      } else {
        // get to home feed
        spa("/home", true, event);
      }
    });
  }
  set_button_status_default(event.target);
};

const log_out = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  await fetch("/logout", {
    method: "PUT",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    // get to frontpage
    spa("/", true, event);
  });
  set_button_status_default(event.target);
};

const post_new_tweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  const form = event.target.form;
  if (is_it_valid(form)) {
    await fetch("/tweets/new", {
      method: "POST",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      set_button_status_default(event.target);
      if (response.redirected && response.url != window.location.href) {
        // if it's been redirected there're errors send with query string
        spa(response.url, true, event);
        return;
      } else {
        // get home feed
        spa("/home", true, event);
      }
    });
  }
};

const put_edited_tweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  const form = event.target.form;
  const tweet_id = event.target.id.slice(2);
  if (is_it_valid(form)) {
    await fetch("/tweets/" + tweet_id, {
      method: "PUT",
      body: new FormData(form),
    }).then((response) => {
      if (!response.ok) {
        return;
      }
      if (response.redirected) {
        // if it's been redirected there're errors send with query string
        spa(response.url, true, event);
      } else {
        // get home feed
        spa("/home", true, event);
      }
    });
  }
  set_button_status_default(event.target);
};

const delete_tweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  const tweet_id = event.target.id.slice(2);
  await fetch("/tweets/delete/" + tweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (!response.ok) {
      set_button_status_default(event.target);
      return;
    }
    if (response.redirected) {
      spa(response.url, false, event);
      set_button_status_default(event.target);
      return;
    }
    // delete tweet and retweets from ui (could be done with spa, but this saves a get request)
    // spa(window.location.pathname, false, event);
    remove_elements_from_ui_by_selector(
      ".tweet_container[data-id='id" + tweet_id + "']"
    );
    remove_elements_from_ui_by_selector(
      ".retweet_container[data-tweet-id='id" + tweet_id + "']"
    );
  });
};

const retweet_tweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  const tweet_id = event.target.dataset.tweetId.slice(2);
  await fetch("/tweets/retweet/" + tweet_id, {
    method: "POST",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    if (response.redirected && response.url != window.location.href) {
      // if it's been redirected there're errors send with query string
      spa(response.url, true, event);
    } else {
      // get home feed
      spa("/home", true, event);
    }
  });
  set_button_status_default(event.target);
};

const delete_retweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  const retweet_id = event.target.dataset.retweetId.slice(2);
  await fetch("/retweets/delete/" + retweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (!response.ok) {
      set_button_status_default(event.target);
      return;
    }
    if (response.redirected) {
      set_button_status_default(event.target);
      spa(response.url, false, event);
      return;
    }
    spa(window.location.pathname, false, event);
  });
};

const toggle_like_tweet = async (event) => {
  stop_event_default(event);
  const tweet_id = event.target.id.slice(4);
  const method = event.target.dataset.liked == "False" ? "POST" : "DELETE";
  const like_buttons = document.querySelectorAll(
    "[data-tweet-id='id" + tweet_id + "'].like_button"
  );
  like_buttons.forEach((button) => {
    set_button_status_processing(button);
  });
  await fetch("/tweets/like/" + tweet_id, {
    method: method,
  }).then((response) => {
    if (!response.ok) {
      event.target.classList.remove("disabled");
      return;
    }
    // only redirected if there's an error
    if (response.redirected) {
      // redirected url will contain error alert message - don't replace state, stay on page
      set_button_status_default(event.target);
      spa(response.url, false);
      return;
    }
    // update ui (could be done with spa, but save the request)
    like_buttons.forEach((button) => {
      if (button.dataset.liked == "False") {
        button.nextElementSibling.textContent =
          parseInt(button.nextElementSibling.textContent) + 1;
      } else {
        button.nextElementSibling.textContent =
          parseInt(button.nextElementSibling.textContent) - 1;
      }
      button.dataset.liked = button.dataset.liked == "True" ? "False" : "True";
      set_button_status_default(button);
    });
    // spa(window.location.pathname, false, event);
  });
};

const view_user = async (event) => {
  stop_event_default(event);
  const username = event.target.dataset.username.slice(2);
  await fetch("/users/" + username, {
    method: "GET",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    if (response.redirected) {
      spa(response.url, true, event);
      return;
    }
    spa("/users/" + username, true, event);
  });
};

const follow_user = async (event) => {
  stop_event_default(event);
  const method = event.target.dataset.follows == "False" ? "POST" : "DELETE";
  const user_id_to_follow = event.target.dataset.userid.slice(2);

  // add elipses to indicate that something is happening
  const follow_buttons = document.querySelectorAll(
    "button[data-userid='id" + user_id_to_follow + "']"
  );
  follow_buttons.forEach((button) => {
    set_button_status_processing(
      button,
      "textProcessing" + button.dataset.follows
    );
  });

  await fetch("/users/follow/" + user_id_to_follow, {
    method: method,
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    if (response.redirected) {
      spa(response.url, true, event);
      event.target.textContent = submit_button_value;
      event.target.classList.remove("disabled");
      return;
    }
    // update the ui (could be done with spa, but save the request)
    // spa(window.location.pathname, false, event);
    follow_buttons.forEach((button) => {
      button.dataset.follows =
        button.dataset.follows == "True" ? "False" : "True";
      set_button_status_default(button, "text" + button.dataset.follows);
    });
  });
};

const open_home = (event) => {
  spa("/home", true, event);
};

const admin_delete_tweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);

  const tweet_id = event.target.id.slice(2);

  await fetch("/admin/delete/" + tweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (!response.ok) {
      return;
    }
    if (response.redirected) {
      spa(response.url, false, event);
      set_button_status_default(event.target);
      return;
    }
    // delete tweet from ui (could be done with spa, but this saves a get request
    // spa("/admin", false, event);
    remove_elements_from_ui_by_selector(
      ".tweet_container[data-id='id" + tweet_id + "']"
    );
  });
};

const remove_selected_image = (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);
  const image_input = document.querySelector("#tweet_image");
  image_input.value = "";
  const image_name_display = document.querySelector("#image_name");
  if (image_input.value == "") {
    image_name_display.value = "No image";
    image_name_display.textContent = "No image";
    document
      .querySelector("label[for='tweet_image']")
      .classList.remove("hidden");
    document.querySelector("#remove_image").classList.add("hidden");
  }
  set_button_status_default(event.target);
};

const tweet_image_changed = (event) => {
  const image_filename = document
    .querySelector("#tweet_image")
    .value.slice(
      document.querySelector("#tweet_image").value.lastIndexOf("\\") + 1
    );
  const image_name_display = document.querySelector("#image_name");
  if (image_filename !== "" && image_filename !== undefined) {
    image_name_display.value = image_filename;
    image_name_display.textContent = image_filename;
    document.querySelector("label[for='tweet_image']").classList.add("hidden");
    document.querySelector("#remove_image").classList.remove("hidden");
  } else {
    image_name_display.value = "No image";
  }
};

const set_button_status_processing = (button, specified_datavalue = null) => {
  if (button.dataset && button.dataset.textProcessing)
    button.textContent = button.dataset.textProcessing;
  if (specified_datavalue != null)
    button.textContent = button.dataset[specified_datavalue];
  button.classList.add("disabled");
};

const set_button_status_default = (button, specified_datavalue = null) => {
  if (button.dataset && button.dataset.text)
    button.textContent = button.dataset.text;
  if (specified_datavalue != null)
    button.textContent = button.dataset[specified_datavalue];
  button.classList.remove("disabled");
};

const stop_event_default = (event) => {
  event.preventDefault();
  event.stopPropagation();
};

const remove_elements_from_ui_by_selector = (selector) => {
  const elements_to_remove = document.querySelectorAll(selector);
  elements_to_remove.forEach((element) => {
    element.remove();
  });
};
