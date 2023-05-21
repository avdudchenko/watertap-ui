export const deleteConfig = (id, name) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/delete?name='+name, {mode: 'cors'});
}; 