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
    const [calories, setCalories] = useState(0);
    const [p1, setP1] = useState('');
    const [p2, setP2] = useState('');
    const [p3, setP3] = useState('');
    const [p1s, setP1s] = useState(0);
    const [p2s, setP2s] = useState(0);
    const [p3s, setP3s] = useState(0);

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
        let portions = []
        if (p1 && p1s)
            portions.push({'portion': p1, weightPerServing: p1s})
        if (p2 && p2s)
            portions.push({'portion': p2, weightPerServing: p2s})
        if (p3 && p3s)
            portions.push({'portion': p3, weightPerServing: p3s})
        props.cb(name, calories, portions)
    };
    const handleChangeName = (event) => {
        console.log("changed: " + event.target.value)
        setName(event.target.value)
    }
    const handleChangeServings = (event) => {
        console.log("changed: " + event.target.value)
        setCalories(event.target.value)
    }
    const handleChangePortionName1 = (event) => {
        console.log("changed: " + event.target.value)
        setP1(event.target.value)
    }
    const handleChangePortionName2 = (event) => {
        console.log("changed: " + event.target.value)
        setP2(event.target.value)
    }
    const handleChangePortionName3 = (event) => {
        console.log("changed: " + event.target.value)
        setP1s(event.target.value)
    }
    const handleChangePortionServings1 = (event) => {
        console.log("changed: " + event.target.value)
        setP1s(event.target.value)
    }
    const handleChangePortionServings2 = (event) => {
        console.log("changed: " + event.target.value)
        setP2s(event.target.value)
    }
    const handleChangePortionServings3 = (event) => {
        console.log("changed: " + event.target.value)
        setP3s(event.target.value)
    }

    return (
        <div>
            <Button variant="outlined" color="primary" onClick={handleClickOpen}>
                Create Meal
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
                        label="Meal name"
                        type="text"
                        onChange={handleChangeName}
                        fullWidth
                    />
                    <TextField
                        // autoFocus
                        margin="dense"
                        id="servings"
                        label="Servings per Meal"
                        type="number"
                        onChange={handleChangeServings}
                        fullWidth
                    />
                    <TextField
                        // autoFocus
                        margin="dense"
                        id="p1"
                        label="Portion 1: Id or Name"
                        type="text"
                        onChange={handleChangePortionName1}
                        fullWidth
                    />
                    <TextField
                        // autoFocus
                        margin="dense"
                        id="p1s"
                        label="Portion 1: Weight per serving"
                        type="number"
                        onChange={handleChangePortionServings1}
                        fullWidth
                    />
                    <TextField
                        // autoFocus
                        margin="dense"
                        id="p2"
                        label="Portion 2: Id or Name"
                        type="text"
                        onChange={handleChangePortionName2}
                        fullWidth
                    />
                    <TextField
                        // autoFocus
                        margin="dense"
                        id="p2s"
                        label="Portion 2: Weight per serving"
                        type="number"
                        onChange={handleChangePortionServings2}
                        fullWidth
                    />
                    <TextField
                        // autoFocus
                        margin="dense"
                        id="p3"
                        label="Portion 3: Id or Name"
                        type="text"
                        onChange={handleChangePortionName3}
                        fullWidth
                    />
                    <TextField
                        // autoFocus
                        margin="dense"
                        id="p3s"
                        label="Portion 3: Weight per serving"
                        type="number"
                        onChange={handleChangePortionServings3}
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