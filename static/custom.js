// let menu=document.getElementsByClassName('sideNavBtn');


//    menu[0].addEventListener('click',showNav);
//    menu[1].addEventListener('click',showNav);


    

// function showNav() {

// let navBarEx= document.getElementById('sideNav');
//     let container =  document.getElementById('resize');
 


// navBarEx.style.height= '100vh';
// navBarEx.style.bottom= '0';
// navBarEx.style.opacity= '1';
// navBarEx.style.transition = 'all 0.6s';

//     if ($('body').width() > 768) {
//     navBarEx.style.width= '20%';
//     container.style.width='80%';
//     container.style.transition= 'width 0.6s';
//     container.style.transitionDelay= '0.6s';

// }
//     else {
//      navBarEx.style.width= '100%';

// }
// menu[1].style.display = 'none';
// menu[0].style.display = 'none';


const form = document.getElementById("my_form");
const radio1 = document.getElementById("customRadio1");
const radio2 = document.getElementById("customRadio2");
const radio3= document.getElementById("customRadio3");
const radio4 = document.getElementById("customRadio4");
const radio5 = document.getElementById("customRadio5");
const radio6 = document.getElementById("customRadio6");
const dropContainer = document.getElementById("dropContainer");
const fileInput = document.getElementById("fileInput");
const fileChosen = document.getElementById('file-chosen');
const alert = document.getElementsByClassName('alert')[0];

alert.addEventListener("animationend", (ev) => {
  if (ev.type === "animationend") {
    alert.style.display = "none";
  }
}, false);

dropContainer.ondragover = dropContainer.ondragenter = function(evt) {
  evt.preventDefault();
};
dropContainer.ondrop = function(evt) {
  // pretty simple -- but not for IE :(
  fileInput.files = evt.dataTransfer.files;

  // If you want to use some of the dropped files
  const dT = new DataTransfer();
  dT.items.add(evt.dataTransfer.files[0]);
  fileInput.files = dT.files;
  fileChosen.textContent = dT.files[0].name
  evt.preventDefault();
};
function submit_form(){
if(radio1.checked){
  form.action = "http://localhost:5000/upload_image";
  return true;
}
else if(radio2.checked){
  form.action = "http://localhost:5000/upload_video";
  return true;
}
else if(radio3.checked){
  form.action = "http://localhost:5000/histogram";
  return true;
}
else if(radio4.checked){
  form.action = "http://localhost:5000/mean_color";
  return true;
}
else if(radio5.checked){
  form.action = "http://localhost:5000/compare_gabor";
  return true;
}
else if(radio6.checked){
  form.action = "http://localhost:5000/compare_videos";
  return true;
}

}

fileInput.addEventListener('change', function(){
  fileChosen.textContent = this.files[0].name
})
// radio1.addEventListener('click',function(){
//   form.action = "http://localhost:5000/upload_image"
// });

// radio2.addEventListener('click',function(){
//   form.action = "http://localhost:5000/upload_video"
// });
// radio3.addEventListener('click',function(){
//   form.action = "http://localhost:5000/histogram"
// });
// radio4.addEventListener('click',function(){
//   form.action = "http://localhost:5000/mean_color"
// });
// radio5.addEventListener('click',function(){
//   form.action = "http://localhost:5000/compare_gabor"
// });
// radio6.addEventListener('click',function(){
//   form.action = "http://localhost:5000/compare_videos"
// });



let closeMenu=document.getElementById('closeBtn');
    
closeMenu.addEventListener('click',closeNav);

function closeNav() {

let closeNavBarEx= document.getElementById('sideNav');
    
    let container =  document.getElementById('resize');



    
closeNavBarEx.style.width= '0';
closeNavBarEx.style.height= '0';
closeNavBarEx.style.bottom= '10%';
closeNavBarEx.style.opacity='0';
closeNavBarEx.style.transition = 'all 0.6s';
closeNavBarEx.style.transitionDelay = '0.3s';

if ($('body').width() > 768) {
    container.style.width='100%';
container.style.transition= 'width 0.6s';
closeNavBarEx.style.transitionDelay= '0.6s';

}
    

menu[1].style.display = 'block';
menu[0].style.display = 'flex';
    
}

$(document).ready(function(){

    $("input[type='radio']").click(function(){
    var sim = $("input[type='radio']:checked").val();
    //alert(sim);
    if (sim<3) { $('.myratings').css('color','red'); $(".myratings").text(sim); }else{ $('.myratings').css('color','green'); $(".myratings").text(sim); } }); });