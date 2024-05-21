import {useState} from "react";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import TextField from "@mui/material/TextField";
import DialogActions from "@mui/material/DialogActions";

const CreatePortionDialog = (props) => {
    const [open, setOpen] = useState(false);
    const [name, setName] = useState('');
    const [calories, setCalories] = useState(0);

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        console.log("name: " + name + " cal: " + calories)
        setOpen(false);
    };
    const handleCloseAndCommit = () => {
        console.log("name: " + name + " cal: " + calories)
        setOpen(false);
        props.cb(name, calories)
    };
    const handleChangeName = (event) => {
        console.log("changed: " + event.target.value)
        setName(event.target.value)
    }
    const handleChangeCal = (event) => {
        console.log("changed: " + event.target.value)
        setCalories(event.target.value)
    }

    return (
        <div>
            <Button variant="outlined" color="primary" onClick={handleClickOpen}>
                Create Portion
            </Button>
            <Dialog open={open} onClose={handleClose} aria-labelledby="form-dialog-title">
                <DialogTitle id="form-dialog-title">New Portion</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Please input elements for your Portion
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="name"
                        label="Portion Name"
                        type="text"
                        onChange={handleChangeName}
                        fullWidth
                    />
                    <TextField
                        // autoFocus
                        margin="dense"
                        id="calories"
                        label="Calories / 100g"
                        type="number"
                        onChange={handleChangeCal}
                        fullWidth
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={handleCloseAndCommit} color="primary">
                        Create
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}

export default CreatePortionDialog;
