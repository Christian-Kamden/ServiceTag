document.addEventListener('DOMContentLoaded',function(){
    const burgerBtn = document.getElementById("burger-btn");
    const navMenu = document.getElementById("nav-menu");

    if(burgerBtn && navMenu){
        burgerBtn.addEventListener('click',function(){
            if(navMenu.style.display === 'none'){
                navMenu.style.display ='block';
            } else {
                navMenu.style.display = 'none';
            }
        });
    }
});