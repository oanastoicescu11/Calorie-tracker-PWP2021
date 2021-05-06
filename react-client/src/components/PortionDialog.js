import {useState} from "react";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogTitle from "@material-ui/core/DialogTitle";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import TextField from "@material-ui/core/TextField";
import DialogActions from "@material-ui/core/DialogActions";

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
                Open form dialog
            </Button>
            <Dialog open={open} onClose={handleClose} aria-labelledby="form-dialog-title">
                <DialogTitle id="form-dialog-title">Subscribe</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Please input elements for your Portion
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="name"
                        label="Name"
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