//Variable selects all elements with form class, for use with adding event listener to form
const form = document.querySelector('.form');
const change = document.getElementById('change');
//Variable selects all elements with send class, for use in determining which radio button is selected
const input = document.querySelector(".send");
//Variables for the textbox where users enter email/phone number and the form submit button
const textbox = document.getElementById("textbox");
const subbut = document.getElementById("subbut");
//Variable where success/failure of form submission will be displayed
let output = document.getElementById('success_fail');
//Regex for use in validating form input for email or phone number
const email_regex =  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
const phone_regex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/im;
//Variables for the email/sms option radio buttons
const email_radio = document.getElementById("email_id");
const sms_radio = document.getElementById("sms_id");

//Clears form 3 seconds after the form is submitted whether successful or not
function formReset() {
  document.getElementById("form1").reset();
  output.innerText = "";
  textbox.hidden=true;
  subbut.hidden= true; change.innerHTML = '';
}

//Whenever an element with the form class is clicked, run the smsORemail function
form.addEventListener('click', smsORemail);

function smsORemail(e) {
  const tgt = e.target;
  if (!tgt.matches("[name=notif]")) return;

  let choice = document.querySelector("input[name=notif]:checked")?.value || "";
  textbox.hidden=true;
  subbut.hidden= true;

  //If neither radio button is selected, end function
  if (!choice) {
    return;
  }

  //Depending on radio button selected, display the text box and submit button. Also change text box label and placeholder.
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

//When the form is submitted, run this function
form.addEventListener('submit', event => {
  event.preventDefault();
  output.innerText = ""
  //Assign form data to var, break out each item in form dict to its' own var
  const formData = new FormData(form);
  const notif_type = formData.get('notif')
  const chk_dog = formData.get('chk_dog')
  const chk_cat = formData.get('chk_cat')
  const comm_textbox = formData.get('comm_textbox')

  //If user tries to submit without typing anything, display this message
  if (comm_textbox === "") {
    output.innerText = "Please enter an email or phone number above.";
    output.style.color = '#ff0000'
    return;
  } 
  //If user tries to submit without selecting dogs or cats, display this message
  else if (!chk_cat && !chk_dog) {
    output.innerText = "Please select which animals you would like to receive notifications for above.";
    output.style.color = '#ff0000'
    return;
  } 
  //If user tries to submit a non-valid email, display this message
  else if (!textbox.value.match(email_regex) && email_radio.checked) {
    alert('Please enter a valid email address.');
    return;
  } 
  //If user tries to submit a non-valid phone #, display this message
  else if (!textbox.value.match(phone_regex) && sms_radio.checked) {
    alert('Please enter a valid phone number.');
    return;
  }

  //Build body of message to send to api. Body is a dictionary which will be converted to a JSON string for transit
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
  
  ///Send form data via POST method to api
  fetch('https://rt4jhd7yf5.execute-api.us-east-1.amazonaws.com/form', {
    isBase64Encoded: false,
    statusCode: '200',
    method: 'POST',
    body: JSON.stringify(body)
  }).then(async res => {
    //Use async to ensure the response is retrieved before code continues.
    //Retrieve response and format it as JS JSON object
    const response = await res.text()
    const response_json = JSON.parse(response)
    console.log(response_json)
    
    //If response shows 200 status code, notify user their form submission was successful
    if (res.status === 200) {
      output.innerText = "Your notification settings have been successfully submitted.";
      output.style.color = '#00cc00';
      
      //If response shows user's email was already in DB, notify them their previous settings will be updated
      if (response_json["Update"] == "true") {
        output.innerText = `You previous notification settings for have been updated.`;
        output.style.color = '#00cc00';
      } else {
        console.log("No update.")
      }
      
      setTimeout(formReset, 3000);
    } 
    //If response doesn't show 200 status code, notify user their form submission failed
    else {
      output.innerText = "The form failed to submit, please try again later.";
      output.style.color = '#ff0000';
      setTimeout(formReset, 3000);
    }
  })
})
