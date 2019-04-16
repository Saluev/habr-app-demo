import React, {Component} from "react";
import {connect} from "react-redux";
import {requestEvents, submitAction} from "../../redux/actions";

class Checkers extends Component {

    componentDidMount() {
        this.props.dispatch(requestEvents(this.props.sessionId));
    }

    render() {
        if (this.props.state === null) {
            return <div>Starting...</div>
        } else {
            let f = this.props.state.field;
            let rows = [];
            for (let i = 0; i < 3; ++i) {
                let cells = [];
                for (let j = 0; j < 3; ++j) {
                    const mark = f[i][j];
                    let onClick = (mark !== "" || !this.props.state.can_make_turn) ? null : () => {
                        this.props.dispatch(submitAction({
                            kind: "turn",
                            i: i,
                            j: j
                        }));
                    };
                    cells.push(<Cell key={j} mark={mark} onClick={onClick}/>);
                }
                rows.push(<div className="checkers-row" key={i}>{cells}</div>);
            }
            return <div className="checkers-field">
                {rows}
            </div>
        }

    }
}

class Cell extends Component {
    render() {
        return <div className="checkers-cell" onClick={this.props.onClick}>{this.props.mark}</div>
    }
}

function mapStateToProps(state) {
    const {page} = state;
    return {
        sessionId: page.session.id,
        roomId: page.room.id,
        state: page.room.state || null,
    };
}

export default connect(mapStateToProps)(Checkers);
