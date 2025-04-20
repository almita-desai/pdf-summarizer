const form=document.getElementById('form')
const Input=document.getElementById('pdfFile')
const result=document.getElementById('output')
const error=document.getElementById('error')

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
        error.innerText=data.error||"an error has occured"
    }
   }

   catch(err){
    error.innerText='Error'
   }
})