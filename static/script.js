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
         result.innerText=data.text
    }
    else{
        result.innerText=data.error||"an error has occured"
    }
   }

   catch(err){
    result.innerText='Error'
   }
})

const show_file_name=()=>{
    let uploaded_file=Input.files[0]
    if(uploaded_file){
        filename.innerText=Input.files[0].name
    }
    else{
        filename.innerText='No file chosen'
    }
}