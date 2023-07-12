const form = document.querySelector('.form');
const change = document.getElementById('change');
const input = document.querySelector(".send");
const textbox = document.getElementById("textbox");
const subbut = document.getElementById("subbut");
let output = document.getElementById('success_fail');
const email_regex =  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
const phone_regex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im;
const email_radio = document.getElementById("email_id");
const sms_radio = document.getElementById("sms_id");

function formReset() {
  document.getElementById("form1").reset();
  output.innerText = "";
  textbox.hidden=true;
  subbut.hidden= true; change.innerHTML = '';
}

form.addEventListener('click', smsORemail);

function smsORemail(e) {
  const tgt = e.target;
  //console.log(tgt)
  if (!tgt.matches("[name=notif]")) return;

  let choice = document.querySelector("input[name=notif]:checked")?.value || "";
  textbox.hidden=true;
  subbut.hidden= true;

  if (!choice) {
    return;
  }

  if (choice === 'email') {
    change.innerHTML = 'Email: ';
    textbox.value = "";
    textbox.placeholder = "john.smith@gmail.com";

  } else if (choice === 'sms') {
    change.innerHTML = 'Phone: ';
    textbox.value = "";
    textbox.placeholder = "555-555-5555";
  }
  subbut.hidden= false;
  textbox.hidden=false;
}

form.addEventListener('submit', event => {
  event.preventDefault();
  output.innerText = ""
  const formData = new FormData(form);
  const notif_type = formData.get('notif')
  const chk_dog = formData.get('chk_dog')
  const chk_cat = formData.get('chk_cat')
  const comm_textbox = formData.get('comm_textbox')
  //const data = Object.fromEntries(formData);

  if (comm_textbox === "") {
    output.innerText = "Please enter an email or phone number above.";
    output.style.color = '#ff0000'
    return;
  } else if (!chk_cat && !chk_dog) {
    output.innerText = "Please select which animals you would like to receive notifications for above.";
    output.style.color = '#ff0000'
    return;
  } else if (!textbox.value.match(email_regex) && email_radio.checked) {
    alert('Please enter a valid email address.');
    return;
  } else if (!textbox.value.match(phone_regex) && sms_radio.checked) {
    alert('Please enter a valid phone number.');
    return;
  }

  let body = {};

  body["comm_type"] = notif_type;
  body["comm_medium"] = comm_textbox;
  if (chk_dog) {
    body["dogs"] = "true";
  } else {
    body["dogs"] = "false";
  }
  if (chk_cat) {
    body["cats"] = "true";
  } else {
    body["cats"] = "false";
  }
  
  fetch('https://rt4jhd7yf5.execute-api.us-east-1.amazonaws.com/form', {
    isBase64Encoded: false,
    statusCode: '200',
    method: 'POST',
    body: JSON.stringify(body)
  }).then(async res => {
    const response = await res.text()
    const response_json = JSON.parse(response)
    console.log(response_json)
    
    if (res.status === 200) {
      output.innerText = "Your notification settings have been successfully submitted.";
      output.style.color = '#00cc00';
      
      if (response_json["Update"] == "true") {
        //output.innerText = `You previous settings for ${comm_medium} have been updated.`;
        output.innerText = `You previous notification settings for have been updated.`;
        output.style.color = '#00cc00';
      } else {
        console.log("No update.")
      }
      
      setTimeout(formReset, 3000);
    } else {
      output.innerText = "The form failed to submit, please try again later.";
      output.style.color = '#ff0000';
      setTimeout(formReset, 3000);
    }
  })
})
