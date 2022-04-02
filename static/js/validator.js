function _all(q, e = document) {
  return e.querySelectorAll(q);
}
function _one(q, e = document) {
  return e.querySelector(q);
}

function validate(form) {
  console.log(form);
  console.log("validate");
  const labels = form.querySelectorAll("label");
  console.log(labels);
  labels.forEach((label) => {
    const input = label.querySelector("input");
    const error = label.querySelector("span.error_message");
    console.log(input.type);
    input.classList.remove("validate_error");
    if (error) {
      console.log(error);
      error.classList.add("hidden");
    }
    if (input.dataset.required && !input.value) {
      //      required
      input.classList.add("validate_error");
      error.classList.remove("hidden");
      error.querySelector("span").textContent = "is required";
    } else if (input.type == "text") {
      if (input.dataset.min && input.dataset.min > input.value.length) {
        //      min length
        input.classList.add("validate_error");
        error.classList.remove("hidden");
        error.querySelector("span").textContent = "is too short";
      } else if (input.dataset.max && input.dataset.max < input.value.length) {
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
  });

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
