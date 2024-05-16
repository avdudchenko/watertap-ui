export const deleteConfig = (id, name) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/'+id+'/delete?name='+name, {mode: 'cors'});
}; 

export const updateNumberOfSubprocesses = (data) => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/update_number_of_subprocesses', {
        method: 'POST',
        mode: 'cors',
        body: JSON.stringify(data)
    });
} 