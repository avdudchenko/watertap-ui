/**
 * Get the name of the project.
 *
 * @returns {Promise<Response>}
 */
export const getProjectName = () => {
    return fetch(process.env.REACT_APP_BACKEND_SERVER+'/flowsheets/project', {mode: 'cors'})
        .then((response) => response.json());
}
