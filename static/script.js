const form=document.getElementById('form')
const Input=document.getElementById('pdfFile')
const result=document.getElementById('output')
const filename=document.getElementById('fileName')

form.addEventListener('submit',async(e)=>{
   e.preventDefault()
   const file=Input.files[0]
   const form_data=new FormData()
   form_data.append('file',file)

   result.textContent='Summarizing...'
   try{
    const response=await fetch('/uploads',{
        method:'POST',
        body:form_data

    })
    const data= await response.json()
    if(response.ok){
        result.style.border="none"
        result.style.textAlign = 'initial';
        result.style.justifyContent = 'initial';
        result.innerText=data.text
        
    }
    else{
        result.style.border="none"
        result.innerText=data.error||"an error has occured"
    }
   }

   catch(err){
    result.style.border="none"
    result.innerText='Error'
   }
})

const show_file_name=()=>{
    let uploaded_file=Input.files[0]
    
    if(uploaded_file){
        console.log('show file name')
        filename.innerText=uploaded_file.name;
    }
    else{
        filename.innerText='No file chosen'
    }
}
result.addEventListener("dragover",(e)=>{
    e.preventDefault()

})
result.addEventListener("drop",(e)=>{
    e.preventDefault()
    Input.files=e.dataTransfer.files
    result.style.border="none"
    show_file_name()

    form.dispatchEvent(new Event('submit'))
})