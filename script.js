// Simple helper
const $ = id => document.getElementById(id);
const form = $('regForm');
const submitBtn = $('submitBtn');
const resetBtn = $('resetBtn');
const topAlert = $('topAlert');
const msg = $('formMessage');

function setTopAlert(text, type){
  topAlert.textContent = text || '';
  topAlert.className = 'alert' + (text ? (type==='error' ? ' error' : ' success') : '');
  topAlert.style.display = text ? 'block' : 'none';
}

// populate countries and phone codes
function populateCountries(){
  const country = $('country');
  const phoneCode = $('phoneCode');
  country.innerHTML = '<option value="">-- Select Country --</option>';
  phoneCode.innerHTML = '<option value="">-- Select Code --</option>';
  DATA.countries.forEach(c=>{
    const opt = document.createElement('option');
    opt.value = c.code; opt.textContent = c.name;
    country.appendChild(opt);

    const pOpt = document.createElement('option');
    pOpt.value = c.phoneCode; pOpt.textContent = `${c.name} (${c.phoneCode})`;
    phoneCode.appendChild(pOpt);
  });
}
function populateStates(){
  const countryVal = $('country').value;
  const state = $('state');
  const city = $('city');
  state.innerHTML = '<option value="">-- Select State --</option>';
  city.innerHTML = '<option value="">-- Select City --</option>';
  if(!countryVal) return;
  const c = DATA.countries.find(x=>x.code===countryVal);
  c.states.forEach(s=>{
    const opt = document.createElement('option'); opt.value = s.name; opt.textContent = s.name;
    state.appendChild(opt);
  });
}
function populateCities(){
  const countryVal = $('country').value;
  const stateVal = $('state').value;
  const city = $('city');
  city.innerHTML = '<option value="">-- Select City --</option>';
  if(!countryVal || !stateVal) return;
  const c = DATA.countries.find(x=>x.code===countryVal);
  const s = c.states.find(x=>x.name===stateVal);
  s.cities.forEach(ci=>{
    const opt = document.createElement('option'); opt.value = ci; opt.textContent = ci;
    city.appendChild(opt);
  });
}

// small helpers
function addInvalid(el, errEl, text){
  if(el) el.classList.add('invalid');
  if(errEl) errEl.textContent = text || '';
}
function clearInvalid(el, errEl){
  if(el) el.classList.remove('invalid');
  if(errEl) errEl.textContent = '';
}

// disposable email check
function isDisposable(email){
  const domain = email.split('@')[1] || '';
  return DATA.disposableDomains.includes(domain.toLowerCase());
}

// phone validation: must start with +code OR accept digits if phoneCode selected separately
function validatePhone(countryCode, phone){
  if(!phone) return false;
  phone = phone.trim();
  // if phone starts with +, check it matches selected phone code
  if(countryCode){
    if(phone.startsWith(countryCode)){
      const rest = phone.slice(countryCode.length).replace(/\D/g,'');
      return rest.length >= 6 && rest.length <= 12;
    }
    // also allow phone field without +code but phoneCode dropdown must match and we accept 7-12 digits
    const digits = phone.replace(/\D/g,'');
    return digits.length >= 7 && digits.length <= 12;
  } else {
    const digits = phone.replace(/\D/g,'');
    return digits.length >= 7 && digits.length <= 12;
  }
}

// password strength
function pwdStrength(password){
  let score = 0;
  if(password.length >= 8) score += 1;
  if(/[A-Z]/.test(password)) score += 1;
  if(/[0-9]/.test(password)) score += 1;
  if(/[^A-Za-z0-9]/.test(password)) score += 1;
  return score; // 0..4
}
function strengthText(s){
  if(s<=1) return 'Weak';
  if(s===2) return 'Medium';
  return 'Strong';
}

function updatePwdMeter(){
  const p = $('password').value;
  const bar = $('pwdMeterBar');
  const text = $('pwdText');
  const s = pwdStrength(p);
  const percent = (s/4)*100;
  bar.style.width = percent + '%';
  text.textContent = `Strength: ${strengthText(s)}`;
  // color variations
  if(s<=1) bar.style.background = 'linear-gradient(90deg,#ff6b6b,#ff9f9f)';
  else if(s===2) bar.style.background = 'linear-gradient(90deg,#ffd166,#ffd966)';
  else bar.style.background = 'linear-gradient(90deg,#b2f5ea,#2ecc71)';
}

// central validation check
function validateForm(showErrors=true){
  let valid = true;
  setTopAlert('', null);
  msg.textContent = ''; msg.style.color = '';

  // first name
  const first = $('firstName');
  if(!first.value.trim()){
    if(showErrors) addInvalid(first, $('firstNameErr'), 'First name is required');
    valid = false;
  } else clearInvalid(first, $('firstNameErr'));

  // last name
  const last = $('lastName');
  if(!last.value.trim()){
    if(showErrors) addInvalid(last, $('lastNameErr'), 'Last name is required');
    valid = false;
  } else clearInvalid(last, $('lastNameErr'));

  // email
  const email = $('email');
  const emailVal = email.value.trim();
  if(!emailVal){
    if(showErrors) addInvalid(email, $('emailErr'), 'Email is required');
    valid = false;
  } else if(!/^\S+@\S+\.\S+$/.test(emailVal)){
    if(showErrors) addInvalid(email, $('emailErr'), 'Enter a valid email');
    valid = false;
  } else if(isDisposable(emailVal)){
    if(showErrors) addInvalid(email, $('emailErr'), 'Disposable emails not allowed');
    valid = false;
  } else clearInvalid(email, $('emailErr'));

  // country/state/city
  const country = $('country'), state = $('state'), city = $('city');
  if(!country.value){ if(showErrors) addInvalid(country, $('countryErr'), 'Country required'); valid=false } else clearInvalid(country, $('countryErr'));
  if(!state.value){ if(showErrors) addInvalid(state, $('stateErr'), 'State required'); valid=false } else clearInvalid(state, $('stateErr'));
  if(!city.value){ if(showErrors) addInvalid(city, $('cityErr'), 'City required'); valid=false } else clearInvalid(city, $('cityErr'));

  // phone
  const phoneCode = $('phoneCode').value || '';
  const phoneEl = $('phone');
  if(!phoneEl.value.trim()){ if(showErrors) addInvalid(phoneEl, $('phoneErr'), 'Phone required'); valid=false; }
  else if(!validatePhone(phoneCode, phoneEl.value)){
    if(showErrors) addInvalid(phoneEl, $('phoneErr'), 'Invalid phone for selected country or format. Start with country code like +91 if shown.');
    valid = false;
  } else clearInvalid(phoneEl, $('phoneErr'));

  // gender
  if(!document.querySelector('input[name="gender"]:checked')){ if(showErrors) $('genderErr').textContent = 'Select gender'; valid=false } else $('genderErr').textContent = '';

  // password
  const p = $('password').value;
  const cp = $('confirmPassword').value;
  const strength = pwdStrength(p);
  if(!p){ if(showErrors) addInvalid($('password'), $('passwordErr'), 'Password required'); valid=false; }
  else if(p.length < 8){ if(showErrors) addInvalid($('password'), $('passwordErr'), 'At least 8 characters'); valid=false; }
  else if(strength < 2){ if(showErrors) addInvalid($('password'), $('passwordErr'), 'Use a stronger password (mix uppercase, digits, symbols)'); valid=false; }
  else clearInvalid($('password'), $('passwordErr'));

  if(cp !== p){ if(showErrors) addInvalid($('confirmPassword'), $('confirmErr'), 'Passwords do not match'); valid=false } else clearInvalid($('confirmPassword'), $('confirmErr'));

  // terms
  if(!$('terms').checked){ if(showErrors) $('termsErr').textContent = 'You must accept terms'; valid=false } else $('termsErr').textContent = '';

  // final
  submitBtn.disabled = !valid;
  return valid;
}

// on submit
form.addEventListener('submit', e=>{
  e.preventDefault();
  const ok = validateForm(true);
  if(!ok){
    setTopAlert('Please fix the highlighted errors and try again.', 'error');
    return;
  }
  // simulate submission (no backend)
  const payload = {
    firstName: $('firstName').value.trim(),
    lastName: $('lastName').value.trim(),
    email: $('email').value.trim(),
    country: $('country').value,
    state: $('state').value,
    city: $('city').value
  };
  setTopAlert('Registration Successful! Your profile has been submitted successfully.', 'success');
  // reset form to show success + cleared fields
  form.reset();
  updatePwdMeter();
  populateCountries(); populateStates(); populateCities();
  submitBtn.disabled = true;
});

// reset
resetBtn.addEventListener('click', ()=>{
  form.reset();
  msg.textContent = '';
  setTopAlert('', null);
  // clear errors and invalid classes
  document.querySelectorAll('.error').forEach(el => el.textContent = '');
  document.querySelectorAll('.invalid').forEach(el => el.classList.remove('invalid'));
  updatePwdMeter();
  submitBtn.disabled = true;
});

// event wiring
window.addEventListener('DOMContentLoaded', ()=>{
  populateCountries();
  populateStates();
  populateCities();
  updatePwdMeter();

  $('country').addEventListener('change', ()=>{
    populateStates();
    populateCities();
    // set phone code
    const c = DATA.countries.find(x=>x.code === $('country').value);
    if(c) $('phoneCode').value = c.phoneCode;
    validateForm(false);
  });

  $('state').addEventListener('change', ()=>{ populateCities(); validateForm(false); });
  $('city').addEventListener('change', ()=> validateForm(false));
  $('phone').addEventListener('input', ()=> validateForm(false));
  $('phoneCode').addEventListener('change', ()=> validateForm(false));

  $('firstName').addEventListener('input', ()=> validateForm(false));
  $('lastName').addEventListener('input', ()=> validateForm(false));
  $('email').addEventListener('input', ()=> validateForm(false));

  $('password').addEventListener('input', ()=>{ updatePwdMeter(); validateForm(false); });
  $('confirmPassword').addEventListener('input', ()=> validateForm(false));

  document.querySelectorAll('input[name="gender"]').forEach(el=>el.addEventListener('change', ()=> validateForm(false)));
  $('terms').addEventListener('change', ()=> validateForm(false));
});

/* Phone validation by country (example for India) */
/* Put this in script.js or in a <script> after your DOM elements load. */

(function () {
  const countryEl = document.getElementById("country");
  const phoneEl = document.getElementById("phone");
  const submitBtn = document.getElementById("submitBtn");

  // create an inline error element if not present
  let phoneErr = document.getElementById("phoneErr");
  if (!phoneErr) {
    phoneErr = document.createElement("div");
    phoneErr.id = "phoneErr";
    phoneErr.className = "error";
    phoneErr.style.display = "none";
    // ensure visible spacing
    phoneErr.style.marginTop = "6px";
    phoneEl.parentNode.insertBefore(phoneErr, phoneEl.nextSibling);
  }

  // helper: extract digits only from the input
  function digitsOnly(s) {
    return (s || "").replace(/\D/g, "");
  }

  // Main phone validation: require exactly 10 numeric digits
  function validatePhone() {
    const raw = (phoneEl.value || "").trim();
    const digits = digitsOnly(raw);

    let ok = false;
    let message = "";

    if (!raw) {
      message = "Phone number is required";
    } else if (!/^\d+$/.test(raw) && digits.length === 0) {
      // input contains no digits at all (e.g., letters)
      message = "Phone number must contain digits only";
    } else if (digits.length !== 10) {
      // not exactly 10 digits
      message = "Phone number must be exactly 10 digits";
    } else {
      // exactly 10 digits -> valid
      ok = true;
    }

    if (ok) {
      phoneEl.classList.remove("invalid");
      phoneErr.style.display = "none";
      phoneErr.textContent = "";
    } else {
      phoneEl.classList.add("invalid");
      phoneErr.style.display = "block";
      phoneErr.textContent = message;
    }

    updateSubmitState();
    return ok;
  }

  // Basic form validity checker (extend as needed)
  function updateSubmitState() {
    const firstOk = (document.getElementById("firstName")?.value || "").trim().length > 0;
    const lastOk = (document.getElementById("lastName")?.value || "").trim().length > 0;
    const emailOk = (document.getElementById("email")?.value || "").trim().length > 0;
    const genderOk = !!document.querySelector('input[name="gender"]:checked');
    const termsOk = !!document.getElementById("terms")?.checked;
    const phoneOk = !phoneEl.classList.contains("invalid") && (phoneEl.value || "").trim().length > 0;

    const passwordOk = (document.getElementById("password")?.value || "").trim().length > 0;
    const confirmOk = (document.getElementById("confirmPassword")?.value || "").trim().length > 0;

    const allOk = firstOk && lastOk && emailOk && genderOk && termsOk && phoneOk && passwordOk && confirmOk;
    if (submitBtn) submitBtn.disabled = !allOk;
  }

  // Wire events
  phoneEl.addEventListener("input", function () {
    validatePhone();
  });

  // re-validate when country is changed (in case you want per-country rules later)
  if (countryEl) {
    countryEl.addEventListener("change", function () {
      validatePhone();
    });
  }

  // Re-evaluate submit state when other fields change
  const otherFields = ["firstName", "lastName", "email", "password", "confirmPassword", "terms"];
  otherFields.forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", updateSubmitState);
      el.addEventListener("change", updateSubmitState);
    }
  });

  // Initial check on page load
  document.addEventListener("DOMContentLoaded", function () {
    validatePhone();
    updateSubmitState();
  });
})();
