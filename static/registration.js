(() => {
 const form=document.getElementById('signup-form');if(!form)return;
 function update(){
  const student=form.querySelector('[name=role]:checked')?.value!=='teacher';
  form.querySelectorAll('.student-only').forEach(n=>{n.hidden=!student;n.querySelectorAll('input').forEach(i=>i.disabled=!student);});
  const email=form.querySelector('[name=email]');if(email)email.required=!student;
  const age=form.querySelector('[name=age]');if(age)age.required=student;
 }
 form.querySelectorAll('[name=role]').forEach(n=>n.addEventListener('change',update));update();
})();
