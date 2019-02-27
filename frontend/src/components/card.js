import React, {Component} from 'react';

class Card extends Component {

    componentDidMount() {
        document.title = this.props.name
    }

    render() {
        const {name, html} = this.props;
        return (
            <div>
                <h1>{name}</h1>
                <div dangerouslySetInnerHTML={{__html: html}}/>
            </div>
        );
    }

}

export default Card;
