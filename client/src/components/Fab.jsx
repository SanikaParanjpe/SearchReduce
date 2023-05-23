import { uploadFile } from '../api/aws';
import { saveS3ObjectName } from '../api/save_s3_object_name';
import plus from '../assets/plus.svg';

export function Fab({getNewData}) {

    function onClick() {
        const input = document.getElementById("input-file");
        input.click();
    }

    async function onChange(file) {
        if (!file) return;
        const response = await uploadFile(file);
        if (response.success) {
            alert("File successfully uploaded: " + response.fileName);
            const res = await saveS3ObjectName(response.fileName);
            if (res) {
                getNewData();
            }
        }
        else {
            alert(response.error);
        }
    }

    return (
        <div className="fab-container" onClick={onClick}>
            <img src={plus} className="fab-plus" alt='' />
            <input type="file" id="input-file" onChange={(e) => onChange(e.target.files[0])} />
        </div>
    );
}