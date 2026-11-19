// Coach Craft email gate settings.
// endpoint: the form URL your email service gives you (Buttondown, Formspree, Mailchimp, etc.).
// Leave it empty and the popup stays off.
window.CC_GATE = {
  endpoint: "",
  field: "email",
  extra: {},
  // MailerLite: endpoint = the form action URL from Forms > Embedded forms,
  // field = "fields[email]", extra = { "ml-submit": "1" }
  title: "Get the Coach Craft library",
  body: "Enter your email to open the guides. You will get occasional updates. Unsubscribe any time.",
  button: "Continue",
  storageKey: "cc_gate_ok"
};
