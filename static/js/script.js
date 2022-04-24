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
      if (response.ok) {
        if (response.redirected) {
          // validation errors sent with query string or send the user to /home
          spa(response.url, true, event);
        } else {
          // go to login
          spa("/login", true, event);
        }
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
      if (response.ok) {
        if (response.redirected) {
          // if it's been redirected there're errors sent with query string
          spa(response.url, true, event);
        } else {
          // success -> go to home feed
          spa("/home", true, event);
        }
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
    if (response.ok) {
      if (response.redirected) {
        // redirected if the user isn't logged in
        spa(response.url, true, event);
      } else {
        // success -> get to frontpage
        spa("/", true, event);
      }
    }
  });

  set_button_status_default(event.target);
};

const submit_tweet_form = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);

  const form = event.target.form;
  const tweet_id = event.target.dataset.tweetId
    ? event.target.dataset.tweetId
    : "new";

  if (is_it_valid(form)) {
    await fetch("/tweets/" + tweet_id, {
      method: event.target.dataset.method,
      body: new FormData(form),
    }).then((response) => {
      console.log(response);
      console.log(response.ok);
      if (response.ok) {
        if (response.redirected) {
          // validation errors send with query string
          spa(response.url, true, event);
        } else {
          // success -> go home feed
          spa("/home", true, event);
        }
      }
    });
  }

  set_button_status_default(event.target);
};

const delete_tweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);

  const tweet_id = event.target.dataset.tweetId;

  await fetch("/tweets/delete/" + tweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (response.ok) {
      if (response.redirected) {
        spa(response.url, false, event);
      } else {
        // delete tweet and retweets from ui (could be done with spa, but this saves a get request)
        // spa(window.location.pathname, false, event);
        remove_elements_from_ui_by_selector(
          ".tweet_container[data-id='id" + tweet_id + "']"
        );
        remove_elements_from_ui_by_selector(
          ".retweet_container[data-tweet-id='" + tweet_id + "']"
        );
      }
    }
  });

  set_button_status_default(event.target);
};

const retweet_tweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);

  const tweet_id = event.target.dataset.tweetId;

  await fetch("/tweets/retweet/" + tweet_id, {
    method: "POST",
  }).then((response) => {
    if (response.ok) {
      if (response.redirected) {
        spa(response.url, true, event);
      } else {
        // reload the ui of the page
        spa(window.location.href, true, event);
      }
    }
  });

  set_button_status_default(event.target);
};

const delete_retweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);

  const retweet_id = event.target.dataset.retweetId;

  await fetch("/retweets/delete/" + retweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (response.ok) {
      if (response.redirected) {
        spa(response.url, false, event);
      } else {
        // reload the ui of the page
        spa(window.location.pathname, false, event);
      }
    }
  });

  set_button_status_default(event.target);
};

const toggle_like_tweet = async (event) => {
  stop_event_default(event);

  const tweet_id = event.target.dataset.tweetId;
  const method = event.target.dataset.liked == "False" ? "POST" : "DELETE";

  // since there can be retweets, there might be multiple like-buttons that needs updating
  const like_buttons = document.querySelectorAll(
    "[data-tweet-id='" + tweet_id + "'].like_button"
  );
  like_buttons.forEach((button) => set_button_status_processing(button));

  await fetch("/tweets/like/" + tweet_id, {
    method: method,
  }).then((response) => {
    if (response.ok) {
      if (response.redirected) {
        // redirected url will contain error alert message - don't replace state, stay on page
        spa(response.url, false);
      } else {
        // update ui (could be done with spa, but save the request)
        // spa(window.location.pathname, false, event);
        like_buttons.forEach((button) => {
          // number of likes
          if (button.dataset.liked == "False") {
            button.nextElementSibling.textContent =
              parseInt(button.nextElementSibling.textContent) + 1;
          } else {
            button.nextElementSibling.textContent =
              parseInt(button.nextElementSibling.textContent) - 1;
          }

          // like status
          button.dataset.liked =
            button.dataset.liked == "True" ? "False" : "True";

          set_button_status_default(button);
        });
      }
    }
  });
};

const follow_user = async (event) => {
  stop_event_default(event);

  const method = event.target.dataset.follows == "False" ? "POST" : "DELETE";
  const user_id_to_follow = event.target.dataset.userId;

  const follow_buttons = document.querySelectorAll(
    "button[data-user-id='" + user_id_to_follow + "']"
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
    if (response.ok) {
      if (response.redirected) {
        spa(response.url, true, event);
      } else {
        if (window.location.pathname.includes("/users/")) {
          // if on user page update ui by spa, to awoid having to updating follower count manually
          spa(window.location.pathname, false, event);
        } else {
          // update the ui (could be done with spa, but save the request)
          // spa(window.location.pathname, false, event);
          follow_buttons.forEach((button) => {
            button.dataset.follows =
              button.dataset.follows == "True" ? "False" : "True";
            set_button_status_default(button, "text" + button.dataset.follows);
          });
        }
      }
    }
  });
};

const admin_delete_tweet = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);

  const tweet_id = event.target.dataset.tweetId;

  await fetch("/admin/delete/" + tweet_id, {
    method: "DELETE",
  }).then((response) => {
    if (response.ok) {
      if (response.redirected) {
        // redirect would be with alert message if an error occured
        spa(response.url, false, event);
      } else {
        // delete tweet from ui (could be done with spa, but this saves a get request)
        // spa("/admin", false, event);
        remove_elements_from_ui_by_selector(
          ".tweet_container[data-tweet-id='" + tweet_id + "']"
        );
      }
    }
  });

  set_button_status_default(event.target);
};

const edit_user = async (event) => {
  stop_event_default(event);
  set_button_status_processing(event.target);

  const form = event.target.form;
  const user_id = event.target.dataset.userId;
  const username = event.target.dataset.username;

  if (is_it_valid(form)) {
    await fetch("/edit/" + user_id, {
      method: "PUT",
      body: new FormData(form),
    }).then((response) => {
      if (response.ok) {
        if (response.redirected) {
          // if it's been redirected there're errors send with query string
          spa(response.url, true, event);
        } else {
          // success -> get user page
          spa(
            "/users/" + form.querySelector("#user_username").value
              ? form.querySelector("#user_username").value
              : username,
            true,
            event
          );
        }
      }
    });
  }
  set_button_status_default(event.target);
};

const remove_selected_image = (event, type) => {
  console.log("remove_selected_image");

  stop_event_default(event);
  set_button_status_processing(event.target);

  const image_name_display = document.querySelector("#image_name");
  const image_input = document.querySelector("#" + type + "_image");
  if (image_input) image_input.value = "";

  if (image_input.value == "") {
    image_name_display.value = "No image";
    image_name_display.textContent = "No image";

    document
      .querySelector("label[for='" + type + "_image']")
      .classList.remove("hidden");

    document.querySelector("#remove_image").classList.add("hidden");
  }

  set_button_status_default(event.target);
};
const image_changed = (event, type) => {
  console.log("tweet_image_changed");
  stop_event_default(event);

  const image_filename = document
    .querySelector("#" + type + "_image")
    .value.slice(
      document.querySelector("#" + type + "_image").value.lastIndexOf("\\") + 1
    );

  const image_name_display = document.querySelector("#image_name");

  if (image_filename !== "" && image_filename !== undefined) {
    image_name_display.value = image_filename;
    image_name_display.textContent = image_filename;
    document
      .querySelector("label[for='" + type + "_image']")
      .classList.add("hidden");
    document.querySelector("#remove_image").classList.remove("hidden");
  } else {
    image_name_display.value = "No image";
  }
};

const set_button_status_processing = (button, specified_datavalue = null) => {
  // set button text till default data-text-processing
  if (button.dataset && button.dataset.textProcessing) {
    button.textContent = button.dataset.textProcessing;
    button.value = button.dataset.textProcessing;
  }
  // set button text to specified data value
  if (specified_datavalue != null) {
    button.textContent = button.dataset[specified_datavalue];
    button.value = button.dataset[specified_datavalue];
  }
  // temporarely disable button
  button.classList.add("disabled");
};
const set_button_status_default = (button, specified_datavalue = null) => {
  // set button text till default data-text
  if (button.dataset && button.dataset.text) {
    button.textContent = button.dataset.text;
    button.value = button.dataset.text;
  }
  // set button text to specified data value
  if (specified_datavalue != null) {
    button.textContent = button.dataset[specified_datavalue];
    button.value = button.dataset[specified_datavalue];
  }
  // make button function again
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
