function _all(q, e = document) {
  return e.querySelectorAll(q);
}
function _one(q, e = document) {
  return e.querySelector(q);
}

function validate(form) {
  //    hide all error messages
  const errors = form.querySelectorAll(".error_message");
  errors.forEach((error) => {
    error.classList.add("hidden");
  });

  //    validate labels
  const labels = form.querySelectorAll("label");
  if (labels) {
    labels.forEach((label) => {
      if (label.control.type !== "file") {
        let input = label.querySelector("input");
        if (input == null) {
          input = label.querySelector("textarea");
        }
        const error = label.querySelector("span.error_to_validate");
        input.classList.remove("validate_error");
        if (error) {
          error.classList.add("hidden");
        } else {
          return true;
        }
        if (input.dataset.required && !input.value) {
          //      required
          input.classList.add("validate_error");
          error.classList.remove("hidden");
          error.querySelector("span").textContent = "is required";
        } else if (
          input.type == "text" ||
          input.type == "password" ||
          input.type == "textarea"
        ) {
          if (input.dataset.min && input.dataset.min > input.value.length) {
            //      min length
            input.classList.add("validate_error");
            error.classList.remove("hidden");
            error.querySelector("span").textContent = "is too short";
          } else if (
            input.dataset.max &&
            input.dataset.max < input.value.length
          ) {
            //      max length
            input.classList.add("validate_error");
            error.classList.remove("hidden");
            error.querySelector("span").textContent = "is too long";
          } else if (
            input.dataset.email &&
            !/^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
              input.value.toLowerCase()
            )
          ) {
            input.classList.add("validate_error");
            error.classList.remove("hidden");
            error.querySelector("span").textContent = "is not valid";
          }
        } else if (input.type == "number") {
          if (
            input.dataset.number &&
            (!/^\d+$/.test(input.value) ||
              parseInt(input.value) < parseInt(input.dataset.min) ||
              parseInt(input.value) > parseInt(input.dataset.min))
          ) {
            input.classList.add("validate_error");
            error.classList.remove("hidden");
            error.querySelector("span").textContent = "is not valid";
          }
        }
      }
    });
  }

  if (!form.querySelector(".validate_error")) {
    return true;
  } else {
    return false;
  }
  // const validate_error = "rgba(240, 130, 240, 0.2)";
  // _all("[data-validate]", form).forEach((element) => {
  //   element.classList.remove("validate_error");
  //   element.style.backgroundColor = "white";
  // });
  // _all("[data-validate]", form).forEach((element) => {
  //   switch (element.getAttribute("data-validate")) {
  //     case "str":
  //       if (
  //         element.value.length < parseInt(element.getAttribute("data-min")) ||
  //         element.value.length > parseInt(element.getAttribute("data-max"))
  //       ) {
  //         element.classList.add("validate_error");
  //         element.style.backgroundColor = validate_error;
  //       }
  //       break;
  //     case "int":
  //       if (
  //         !/^\d+$/.test(element.value) ||
  //         parseInt(element.value) <
  //           parseInt(element.getAttribute("data-min")) ||
  //         parseInt(element.value) > parseInt(element.getAttribute("data-max"))
  //       ) {
  //         element.classList.add("validate_error");
  //         element.style.backgroundColor = validate_error;
  //       }
  //       break;
  //     case "email":
  //       let re =
  //         /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  //       if (!re.test(element.value.toLowerCase())) {
  //         element.classList.add("validate_error");
  //         element.style.backgroundColor = validate_error;
  //       }
  //       break;
  //     case "re":
  //       var regex = new RegExp(element.getAttribute("data-re"));
  //       if (!regex.test(element.value)) {
  //         console.log("phone error");
  //         element.classList.add("validate_error");
  //         element.style.backgroundColor = validate_error;
  //       }
  //       break;
  //     case "match":
  //       if (
  //         element.value !=
  //         _one(`[name='${element.getAttribute("data-match-name")}']`, form)
  //           .value
  //       ) {
  //         element.classList.add("validate_error");
  //         element.style.backgroundColor = validate_error;
  //       }
  //       break;
  //   }
  // });
  // if (!_one(".validate_error", form)) {
  //   callback();
  //   return;
  // }
  // _one(".validate_error", form).focus()
}
