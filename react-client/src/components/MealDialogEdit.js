import {useState} from "react";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogTitle from "@material-ui/core/DialogTitle";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import TextField from "@material-ui/core/TextField";
import DialogActions from "@material-ui/core/DialogActions";

const MealDialog = (props) => {
    const [open, setOpen] = useState(false);
    const [name, setName] = useState('');

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const handleCloseAndCommit = () => {
        setOpen(false);
        props.cb(props.meal, name)
    };
    const handleChangeName = (event) => {
        console.log("changed: " + event.target.value)
        setName(event.target.value)
    }

    return (
        <div>
            <Button variant="outlined" color="primary" onClick={handleClickOpen}>
                Rename
            </Button>
            <Dialog open={open} onClose={handleClose} aria-labelledby="form-dialog-title">
                <DialogTitle id="form-dialog-title">{props.meal.name}</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Please input new name for your Meal
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="name"
                        label="Meal name"
                        // value={props.meal.name}
                        type="text"
                        onChange={handleChangeName}
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

export default MealDialog;