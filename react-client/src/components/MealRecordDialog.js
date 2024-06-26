import {useState} from "react";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import TextField from "@mui/material/TextField";
import DialogActions from "@mui/material/DialogActions";

const MealRecordDialog = (props) => {
    const [open, setOpen] = useState(false);
    const [name, setName] = useState('');
    const [servings, setServings] = useState(0);
    const [datetime, setDatetime] = useState(Date.now);

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const handleCloseAndCommit = () => {
        console.log("name: " + name + " servings: " + servings + " datetime: " + datetime)
        setOpen(false);
        props.cb(name, servings, datetime)
    };
    const handleChangeName = (event) => {
        console.log("changed: " + event.target.value)
        setName(event.target.value)
    }
    const handleChangeServings = (event) => {
        console.log("changed: " + event.target.value)
        setServings(event.target.value)
    }
    const handleChangeDateTime = (event) => {
        console.log("changed: " + event.target.value)
        setDatetime(event.target.value)
    }

    return (
        <div>
            <Button variant="outlined" color="primary" onClick={handleClickOpen}>
                Record a Meal
            </Button>
            <Dialog open={open} onClose={handleClose} aria-labelledby="form-dialog-title">
                <DialogTitle id="form-dialog-title">Subscribe</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Please input elements for your Meal
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="name"
                        label="Meal ID"
                        type="text"
                        onChange={handleChangeName}
                        fullWidth
                    />
                    <TextField
                        margin="dense"
                        id="servings"
                        label="Servings consumed"
                        type="number"
                        onChange={handleChangeServings}
                        fullWidth
                    />
                    <TextField
                        id="datetime-local"
                        label="Consumption time"
                        type="datetime-local"
                        defaultValue="2021-05-08T10:30"
                        onChange={handleChangeDateTime}
                        InputLabelProps={{
                            shrink: true,
                        }}
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

export default MealRecordDialog;
