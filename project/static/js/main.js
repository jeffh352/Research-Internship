const apiData = {
    url: 'https://data.bioontology.org/ontologies/',
    type: 'BRO',
}

const {url, type} = apiData
const apiUrl = `${url}${type}`

console.log(apiUrl)
fetch(apiUrl)
    .then( (data)=> data.json())